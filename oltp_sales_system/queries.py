"""
Demonstration of the two required queries for OLTP Sales System using SQLAlchemy
"""
from sqlalchemy import text
from config import engine
from datetime import datetime, timedelta

def get_sales_by_product_location_time(product_id, location_id, start_date, end_date):
    """
    Query 1: Sales for a given product by location over a period of time
    
    Returns aggregated sales metrics for a specific product at a specific location
    within a date range.
    """
    try:
        with engine.connect() as connection:
            query = text("""
                SELECT 
                    p.product_id,
                    p.product_name,
                    p.category,
                    p.brand,
                    l.location_id,
                    l.location_name,
                    l.city,
                    l.country,
                    COUNT(*) AS number_of_sales,
                    SUM(s.quantity) AS total_quantity_sold,
                    SUM(s.total_amount) AS total_revenue,
                    AVG(s.total_amount) AS avg_sale_amount,
                    MIN(s.total_amount) AS min_sale_amount,
                    MAX(s.total_amount) AS max_sale_amount,
                    MIN(s.sale_timestamp) AS first_sale_date,
                    MAX(s.sale_timestamp) AS last_sale_date
                FROM sales s
                JOIN product p ON s.product_id = p.product_id
                JOIN location l ON s.location_id = l.location_id
                WHERE p.product_id = :product_id
                  AND l.location_id = :location_id
                  AND s.sale_timestamp BETWEEN :start_date AND :end_date
                GROUP BY 
                    p.product_id, p.product_name, p.category, p.brand,
                    l.location_id, l.location_name, l.city, l.country
            """)
            
            result = connection.execute(query, {
                'product_id': product_id,
                'location_id': location_id,
                'start_date': start_date,
                'end_date': end_date
            })
            
            row = result.fetchone()
            if row:
                columns = [key for key in result.keys()]
                return dict(zip(columns, row))
            
            return None
        
    except Exception as e:
        print(f"Error executing query: {e}")
        return None

def get_max_sales_for_product_location(product_id, location_id, start_date, end_date):
    """
    Query 2: Maximum number of sales for a given product over time for a given location
    
    Returns the date with the maximum number of sales for a product at a location,
    along with daily sales statistics.
    """
    try:
        with engine.connect() as connection:
            # Get daily sales aggregated
            query = text("""
                SELECT 
                    p.product_id,
                    p.product_name,
                    l.location_id,
                    l.location_name,
                    DATE(s.sale_timestamp) AS sale_date,
                    COUNT(*) AS number_of_sales,
                    SUM(s.quantity) AS total_quantity,
                    SUM(s.total_amount) AS daily_revenue
                FROM sales s
                JOIN product p ON s.product_id = p.product_id
                JOIN location l ON s.location_id = l.location_id
                WHERE p.product_id = :product_id
                  AND l.location_id = :location_id
                  AND s.sale_timestamp BETWEEN :start_date AND :end_date
                GROUP BY 
                    p.product_id, p.product_name,
                    l.location_id, l.location_name,
                    DATE(s.sale_timestamp)
                ORDER BY number_of_sales DESC, daily_revenue DESC
                LIMIT 1
            """)
            
            result = connection.execute(query, {
                'product_id': product_id,
                'location_id': location_id,
                'start_date': start_date,
                'end_date': end_date
            })
            max_day_row = result.fetchone()
            max_day = None
            if max_day_row:
                columns = [key for key in result.keys()]
                max_day = dict(zip(columns, max_day_row))
            
            # Also get overall statistics
            stats_query = text("""
                SELECT 
                    CAST(COUNT(*) AS SIGNED) AS total_sales,
                    CAST(COUNT(DISTINCT sale_date) AS SIGNED) AS days_with_sales,
                    AVG(daily_sales) AS avg_daily_sales,
                    MAX(daily_sales) AS max_daily_sales
                FROM (
                    SELECT DATE(sale_timestamp) AS sale_date, COUNT(*) AS daily_sales
                    FROM sales
                    WHERE product_id = :product_id
                      AND location_id = :location_id
                      AND sale_timestamp BETWEEN :start_date AND :end_date
                    GROUP BY DATE(sale_timestamp)
                ) AS daily_stats
            """)
            
            result = connection.execute(stats_query, {
                'product_id': product_id,
                'location_id': location_id,
                'start_date': start_date,
                'end_date': end_date
            })
            stats_row = result.fetchone()
            stats = None
            if stats_row:
                stats_columns = [key for key in result.keys()]
                stats = dict(zip(stats_columns, stats_row))
            
            return {
                'max_sales_day': max_day,
                'overall_stats': stats
            }
        
    except Exception as e:
        print(f"Error executing query: {e}")
        return None

def demonstrate_queries():
    """Run demonstration queries with sample data"""
    print("=" * 80)
    print("OLTP Sales System - Query Demonstrations")
    print("=" * 80)
    
    # Get some sample product and location IDs
    try:
        with engine.connect() as connection:
            # Get a random product/location combination that actually has sales
            result = connection.execute(text("""
                SELECT 
                    p.product_id, 
                    p.product_name,
                    l.location_id,
                    l.location_name,
                    COUNT(*) as sales_count
                FROM sales s
                JOIN product p ON s.product_id = p.product_id
                JOIN location l ON s.location_id = l.location_id
                GROUP BY p.product_id, p.product_name, l.location_id, l.location_name
                HAVING sales_count >= 3
                ORDER BY RAND()
                LIMIT 1
            """))
            row = result.fetchone()
            
            if not row:
                print("No sales data found. Please run sample_data.py first.")
                return
                
            product = {'product_id': row[0], 'product_name': row[1]}
            location = {'location_id': row[2], 'location_name': row[3]}
        
        product_id = product['product_id']
        location_id = location['location_id']
        
        # Date range: last 2 years (matching the sample data)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=730)
        
        print(f"\nSample Query Parameters:")
        print(f"  Product: {product['product_name']} (ID: {product_id})")
        print(f"  Location: {location['location_name']} (ID: {location_id})")
        print(f"  Date Range: {start_date.date()} to {end_date.date()}")
        print()
        
        # ========================================
        # Query 1 Demonstration
        # ========================================
        print("\n" + "=" * 80)
        print("QUERY 1: Sales for product by location over time period")
        print("=" * 80)
        
        result1 = get_sales_by_product_location_time(
            product_id, 
            location_id, 
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )
        
        if result1:
            print(f"\nProduct: {result1['product_name']} ({result1['category']} - {result1['brand']})")
            print(f"Location: {result1['location_name']}, {result1['city']}, {result1['country']}")
            print(f"\nSales Metrics:")
            print(f"  Total Number of Sales: {result1['number_of_sales']}")
            print(f"  Total Quantity Sold: {result1['total_quantity_sold']}")
            print(f"  Total Revenue: ${result1['total_revenue']:,.2f}")
            print(f"  Average Sale Amount: ${result1['avg_sale_amount']:,.2f}")
            print(f"  Min Sale Amount: ${result1['min_sale_amount']:,.2f}")
            print(f"  Max Sale Amount: ${result1['max_sale_amount']:,.2f}")
            print(f"  First Sale: {result1['first_sale_date']}")
            print(f"  Last Sale: {result1['last_sale_date']}")
        else:
            print("No sales found for this product/location combination in the date range.")
        
        # ========================================
        # Query 2 Demonstration
        # ========================================
        print("\n" + "=" * 80)
        print("QUERY 2: Maximum number of sales for product at location")
        print("=" * 80)
        
        result2 = get_max_sales_for_product_location(
            product_id,
            location_id,
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )
        
        if result2 and result2['max_sales_day']:
            max_day = result2['max_sales_day']
            stats = result2['overall_stats']
            
            print(f"\nProduct: {max_day['product_name']}")
            print(f"Location: {max_day['location_name']}")
            print(f"\nPeak Sales Day:")
            print(f"  Date: {max_day['sale_date']}")
            print(f"  Number of Sales: {max_day['number_of_sales']}")
            print(f"  Total Quantity: {max_day['total_quantity']}")
            print(f"  Daily Revenue: ${max_day['daily_revenue']:,.2f}")
            
            print(f"\nOverall Statistics:")
            print(f"  Total Sales (Period): {stats['total_sales']}")
            print(f"  Days with Sales: {stats['days_with_sales']}")
            print(f"  Average Daily Sales: {stats['avg_daily_sales']:.2f}")
            print(f"  Maximum Daily Sales: {stats['max_daily_sales']}")
        else:
            print("No sales found for this product/location combination in the date range.")
        
        print("\n" + "=" * 80)
        print("Query demonstrations completed!")
        print("=" * 80)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    demonstrate_queries()
