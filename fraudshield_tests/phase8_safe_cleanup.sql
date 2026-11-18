SET LOCAL lock_timeout = '5s';

LOCK TABLE public.transactions, public.predictions,
    public.alerts IN SHARE ROW EXCLUSIVE MODE;

DO $verify$
DECLARE
    removed_count INTEGER;
BEGIN
    IF current_database() <> 'fraudshield_db'
       OR current_user <> 'fraudshield_app' THEN
        RAISE EXCEPTION 'Wrong database connection';
    END IF;

    IF (SELECT COUNT(*) FROM public.transactions) <> 2
       OR (SELECT COUNT(*) FROM public.predictions) <> 2
       OR (SELECT COUNT(*) FROM public.alerts) <> 1 THEN
        RAISE EXCEPTION 'Unexpected record counts';
    END IF;

    IF (SELECT COUNT(*) FROM public.transactions
        WHERE id = '9fa3b1f6-48d4-584b-a807-ef5158d8b7a5') <> 1 THEN
        RAISE EXCEPTION 'Test transaction not found';
    END IF;

    IF (SELECT COUNT(*) FROM public.predictions
        WHERE id = 'a4471366-33be-46b2-b668-64a19ab4c1e9'
          AND transaction_id = '9fa3b1f6-48d4-584b-a807-ef5158d8b7a5'
          AND reasons_json::jsonb ->> 'model_version'
              = 'random-forest-v1') <> 1 THEN
        RAISE EXCEPTION 'Prediction relationship mismatch';
    END IF;

    IF EXISTS (
        SELECT 1 FROM public.alerts
        WHERE transaction_id = '9fa3b1f6-48d4-584b-a807-ef5158d8b7a5'
    ) THEN
        RAISE EXCEPTION 'Unexpected linked alert';
    END IF;

    DELETE FROM public.predictions
    WHERE id = 'a4471366-33be-46b2-b668-64a19ab4c1e9'
      AND transaction_id = '9fa3b1f6-48d4-584b-a807-ef5158d8b7a5';

    GET DIAGNOSTICS removed_count = ROW_COUNT;

    IF removed_count <> 1 THEN
        RAISE EXCEPTION 'Prediction deletion mismatch';
    END IF;

    DELETE FROM public.transactions
    WHERE id = '9fa3b1f6-48d4-584b-a807-ef5158d8b7a5';

    GET DIAGNOSTICS removed_count = ROW_COUNT;

    IF removed_count <> 1 THEN
        RAISE EXCEPTION 'Transaction deletion mismatch';
    END IF;

    IF (SELECT COUNT(*) FROM public.transactions) <> 1
       OR (SELECT COUNT(*) FROM public.predictions) <> 1
       OR (SELECT COUNT(*) FROM public.alerts) <> 1 THEN
        RAISE EXCEPTION 'Original counts not restored';
    END IF;
END
$verify$;

SELECT 'transactions' AS table_name, COUNT(*) FROM public.transactions
UNION ALL
SELECT 'predictions', COUNT(*) FROM public.predictions
UNION ALL
SELECT 'alerts', COUNT(*) FROM public.alerts;