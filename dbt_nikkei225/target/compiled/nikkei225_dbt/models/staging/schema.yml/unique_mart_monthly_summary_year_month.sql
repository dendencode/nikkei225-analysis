
    
    

select
    year_month as unique_field,
    count(*) as n_records

from main."mart_monthly_summary"
where year_month is not null
group by year_month
having count(*) > 1


