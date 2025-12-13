import pandas as pd

def calculate_probabilities(df):
    """
    Calculates P(Dimension | Product) for each product and feedback dimension.
    
    Args:
        df (pd.DataFrame): DataFrame containing 'Product' and 'Feedback Type'.
        
    Returns:
        pd.DataFrame: DataFrame with probabilities.
    """
    if df.empty:
        return pd.DataFrame()

    # Calculate counts
    total_counts = df.groupby('Product').size().reset_index(name='Total Feedback Count')
    dimension_counts = df.groupby(['Product', 'Feedback Type']).size().reset_index(name='Count')
    
    # Merge to get totals for each product
    merged = pd.merge(dimension_counts, total_counts, on='Product')
    
    # Calculate probability
    merged['Probability'] = merged['Count'] / merged['Total Feedback Count']
    
    # Pivot to get columns for each dimension
    pivot_df = merged.pivot(index='Product', columns='Feedback Type', values='Probability').reset_index()
    pivot_df = pivot_df.fillna(0) # Fill NaNs with 0
    
    # Rename columns for clarity
    pivot_df.columns.name = None
    pivot_df = pivot_df.rename(columns={
        'Availability': 'Probability of Availability Issues',
        'Transaction Success': 'Probability of Transaction Success Issues',
        'Satisfaction': 'Probability of Satisfaction Issues'
    })
    
    # Add Total Feedback Count back
    final_df = pd.merge(pivot_df, total_counts, on='Product')
    
    return final_df
