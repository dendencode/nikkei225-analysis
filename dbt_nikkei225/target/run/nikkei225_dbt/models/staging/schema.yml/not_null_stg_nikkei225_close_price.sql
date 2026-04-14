
    select
      count(*) as failures,
      case when count(*) != 0
        then 'true' else 'false' end as should_warn,
      case when count(*) != 0
        then 'true' else 'false' end as should_error
    from (
      
    
  
    
    



select close_price
from main."stg_nikkei225"
where close_price is null



  
  
      
    ) dbt_internal_test