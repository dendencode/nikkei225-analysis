
    
    

select
    date as unique_field,
    count(*) as n_records

from main."int_daily_metrics"
where date is not null
group by date
having count(*) > 1


