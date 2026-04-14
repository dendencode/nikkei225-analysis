
    select
      count(*) as failures,
      case when count(*) != 0
        then 'true' else 'false' end as should_warn,
      case when count(*) != 0
        then 'true' else 'false' end as should_error
    from (
      
    
  
    
    

select
    date as unique_field,
    count(*) as n_records

from main."stg_nikkei225"
where date is not null
group by date
having count(*) > 1



  
  
      
    ) dbt_internal_test