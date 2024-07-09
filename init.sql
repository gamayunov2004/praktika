CREATE TABLE IF NOT EXISTS hhru_table (
    title text,
    requirement text,
    city text,
    salary_from int,
    salary_to int,
    employment text,
    schedule text,
    vacancy_url text UNIQUE
);