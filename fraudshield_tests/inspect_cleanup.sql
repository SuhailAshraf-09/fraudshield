SELECT current_database(), current_user;

SELECT 'transactions' AS table_name, COUNT(*) AS records
FROM public.transactions
UNION ALL
SELECT 'predictions', COUNT(*)
FROM public.predictions
UNION ALL
SELECT 'alerts', COUNT(*)
FROM public.alerts;

SELECT table_name, column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name IN ('transactions', 'predictions', 'alerts')
ORDER BY table_name, ordinal_position;

SELECT conrelid::regclass AS table_name,
       conname AS constraint_name,
       pg_get_constraintdef(oid) AS definition
FROM pg_constraint
WHERE contype = 'f'
  AND conrelid IN (
      'public.predictions'::regclass,
      'public.alerts'::regclass
  );
