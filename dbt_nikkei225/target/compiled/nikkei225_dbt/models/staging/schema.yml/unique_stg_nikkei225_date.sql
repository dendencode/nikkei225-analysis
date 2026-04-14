
    
    

select
    date as unique_field,
    count(*) as n_records

from main."stg_nikkei225"
where date is not null
group by date
having count(*) > 1


