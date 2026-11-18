SET LOCAL lock_timeout = '5s';

LOCK TABLE
    public.transactions,
    public.predictions,
    public.alerts
IN SHARE ROW EXCLUSIVE MODE;

DO $cleanup$
DECLARE
    removed_count INTEGER;
BEGIN
    IF current_database() <> 'fraudshield_db'
       OR current_user <> 'fraudshield_app' THEN
        RAISE EXCEPTION 'Incorrect database connection';
    END IF;

    IF (SELECT COUNT(*) FROM public.transactions) <> 2
       OR (SELECT COUNT(*) FROM public.predictions) <> 2
       OR (SELECT COUNT(*) FROM public.alerts) <> 2 THEN
        RAISE EXCEPTION 'Unexpected database record counts';
    END IF;

    IF (SELECT COUNT(*) FROM public.transactions
        WHERE id = '106fe772-a9d7-5658-88c8-b8955b58c2fc') <> 1 THEN
        RAISE EXCEPTION 'Test transaction not found';
    END IF;

    IF (SELECT COUNT(*) FROM public.predictions
        WHERE id = 'd4aa458a-ea6a-476c-a7d8-86d49409d36f'
          AND transaction_id = '106fe772-a9d7-5658-88c8-b8955b58c2fc'
          AND risk_tier = 'HIGH'
          AND reasons_json::jsonb ->> 'model_version'
              = 'random-forest-v1'
          AND reasons_json::jsonb ->> 'classification'
              = 'FLAGGED') <> 1 THEN
        RAISE EXCEPTION 'Prediction verification failed';
    END IF;

    IF (SELECT COUNT(*) FROM public.alerts
        WHERE transaction_id = '106fe772-a9d7-5658-88c8-b8955b58c2fc'
          AND status = 'open'
          AND priority = 'high') <> 1
       OR (SELECT COUNT(*) FROM public.alerts
        WHERE transaction_id = '106fe772-a9d7-5658-88c8-b8955b58c2fc') <> 1 THEN
        RAISE EXCEPTION 'Fraud alert verification failed';
    END IF;

    DELETE FROM public.alerts
    WHERE transaction_id = '106fe772-a9d7-5658-88c8-b8955b58c2fc';

    GET DIAGNOSTICS removed_count = ROW_COUNT;
    IF removed_count <> 1 THEN
        RAISE EXCEPTION 'Alert deletion count mismatch';
    END IF;

    DELETE FROM public.predictions
    WHERE id = 'd4aa458a-ea6a-476c-a7d8-86d49409d36f'
      AND transaction_id = '106fe772-a9d7-5658-88c8-b8955b58c2fc';

    GET DIAGNOSTICS removed_count = ROW_COUNT;
    IF removed_count <> 1 THEN
        RAISE EXCEPTION 'Prediction deletion count mismatch';
    END IF;

    DELETE FROM public.transactions
    WHERE id = '106fe772-a9d7-5658-88c8-b8955b58c2fc';

    GET DIAGNOSTICS removed_count = ROW_COUNT;
    IF removed_count <> 1 THEN
        RAISE EXCEPTION 'Transaction deletion count mismatch';
    END IF;

    IF (SELECT COUNT(*) FROM public.transactions) <> 1
       OR (SELECT COUNT(*) FROM public.predictions) <> 1
       OR (SELECT COUNT(*) FROM public.alerts) <> 1 THEN
        RAISE EXCEPTION 'Original record counts not restored';
    END IF;
END
$cleanup$;

SELECT 'transactions' AS table_name, COUNT(*) AS records
FROM public.transactions
UNION ALL
SELECT 'predictions', COUNT(*)
FROM public.predictions
UNION ALL
SELECT 'alerts', COUNT(*)
FROM public.alerts;