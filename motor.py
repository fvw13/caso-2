import pandas as pd

def get_insights(df):
    insights_list = []
    
    # Agrupar para detectar tendencias y anomalías
    for (zone, metric), group in df.groupby(['ZONE', 'METRIC']):
        group = group.sort_values('WEEK_NUM') # De L8W a L0W
        values = group['VALUE'].tolist()
        
        # 1. Anomalías (>10% cambio en la última semana) [cite: 31]
        if len(values) >= 2:
            change = (values[-1] - values[-2]) / (values[-2] if values[-2] != 0 else 1)
            if abs(change) > 0.10:
                insights_list.append({
                    "Categoría": "Anomalía",
                    "Zona": zone,
                    "Métrica": metric,
                    "Detalle": f"{'Mejora' if change > 0 else 'Deterioro'} del {abs(change):.1%} en L0W."
                })
        
        # 2. Tendencias preocupantes (3+ semanas cayendo) [cite: 32]
        if len(values) >= 4:
            if values[-1] < values[-2] < values[-3] < values[-4]:
                insights_list.append({
                    "Categoría": "Tendencia Preocupante",
                    "Zona": zone,
                    "Métrica": metric,
                    "Detalle": "Caída consecutiva en las últimas 4 semanas."
                })
                
    return pd.DataFrame(insights_list)