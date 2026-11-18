BEGIN;

SET LOCAL lock_timeout = '5s';

LOCK TABLE
    public.transactions,
    public.predictions,
    public.alerts
IN SHARE ROW EXCLUSIVE MODE;

DO $fraudshield$
DECLARE
    target_id VARCHAR;
    matched_count INTEGER;
BEGIN
    IF current_database() <> 'fraudshield_db'
       OR current_user <> 'fraudshield_app' THEN
        RAISE EXCEPTION 'Incorrect database identity';
    END IF;

    IF (SELECT COUNT(*) FROM public.transactions) <> 2
       OR (SELECT COUNT(*) FROM public.predictions) <> 2
       OR (SELECT COUNT(*) FROM public.alerts) <> 1 THEN
        RAISE EXCEPTION 'Database counts changed: cleanup cancelled';
    END IF;

    SELECT COUNT(*), MIN(t.id)
    INTO matched_count, target_id
    FROM public.transactions t
    WHERE EXISTS (
        SELECT 1
        FROM jsonb_each_text(to_jsonb(t)) AS field
        WHERE field.value = 'FSTEST86c2668aa32d'
    );

    IF matched_count <> 1 THEN
        RAISE EXCEPTION 'Unique test transaction not found';
    END IF;

    IF (
        SELECT COUNT(*)
        FROM public.predictions
        WHERE transaction_id = target_id
    ) <> 1 THEN
        RAISE EXCEPTION 'Expected linked prediction missing';
    END IF;

    IF (
        SELECT COUNT(*)
        FROM public.alerts
        WHERE transaction_id = target_id
    ) <> 0 THEN
        RAISE EXCEPTION 'Unexpected linked alert: cleanup cancelled';
    END IF;

    DELETE FROM public.predictions
    WHERE transaction_id = target_id;

    DELETE FROM public.transactions
    WHERE id = target_id;

    IF (SELECT COUNT(*) FROM public.transactions) <> 1
       OR (SELECT COUNT(*) FROM public.predictions) <> 1
       OR (SELECT COUNT(*) FROM public.alerts) <> 1 THEN
        RAISE EXCEPTION 'Original counts not restored';
    END IF;
END
$fraudshield$;

COMMIT;

SELECT 'transactions' AS table_name, COUNT(*) AS records
FROM public.transactions
UNION ALL
SELECT 'predictions', COUNT(*)
FROM public.predictions
UNION ALL
SELECT 'alerts', COUNT(*)
FROM public.alerts;