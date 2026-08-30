-- BENCHMARK: sqlite3 :memory: < fib.sql
WITH RECURSIVE fibonacci(n, a, b) AS (
    -- Seed values
    SELECT 0, 0, 1

    UNION ALL

    -- Loop 100,000,000 times.
    -- The modulo keeps the integers safely within 64-bit bounds.
    SELECT n + 1, b, (a + b) % 1000000007
    FROM fibonacci
    WHERE n < 100000000
)
-- Only output the final computed value to avoid terminal I/O bottlenecks
SELECT a FROM fibonacci WHERE n = 100000000;
