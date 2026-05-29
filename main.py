#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SIMULACIÓN MONTE CARLO - MUNDIAL FIFA 2026
Universidad Católica Boliviana "San Pablo" - Regional Cochabamba
Investigación Operativa II

Autor: Jorge Vargas Poquechoque
Fecha: 26 de mayo de 2026
"""

import os
import sys
import time
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Agregar src al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.team import Team
from src.monte_carlo import MonteCarloSimulation

def setup_directories():
    """Crea los directorios necesarios si no existen"""
    directories = ['data', 'src', 'results', 'figures']
    for dir_name in directories:
        Path(dir_name).mkdir(exist_ok=True)

def plot_results(results, num_simulations):
    """Genera gráficos de los resultados"""
    
    total_sims = sum(results['champion'].values())
    if total_sims == 0:
        print("⚠️ No hay datos suficientes para generar gráficos.")
        return
    
    # Configurar estilo
    plt.style.use('seaborn-v0_8-darkgrid')
    sns.set_palette("husl")
    
    # Gráfico 1: Top 10 probabilidades de campeón
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle(f'Resultados Simulación Monte Carlo - Mundial FIFA 2026\n({total_sims} simulaciones exitosas)', 
                 fontsize=16, fontweight='bold')
    
    # 1. Probabilidades de campeón
    champions = sorted(results['champion'].items(), key=lambda x: x[1], reverse=True)[:10]
    if champions:
        teams = [t[0] for t in champions]
        probs = [(t[1]/total_sims)*100 for t in champions]
        
        axes[0, 0].barh(teams, probs, color='gold', edgecolor='black')
        axes[0, 0].set_xlabel('Probabilidad (%)', fontsize=11)
        axes[0, 0].set_title('Top 10 - Probabilidad de Ser Campeón', fontsize=12, fontweight='bold')
        axes[0, 0].invert_yaxis()
        
        for i, (team, prob) in enumerate(zip(teams, probs)):
            axes[0, 0].text(prob + 0.5, i, f'{prob:.1f}%', va='center', fontsize=9)
    else:
        axes[0, 0].text(0.5, 0.5, 'Sin datos suficientes', ha='center', va='center', transform=axes[0, 0].transAxes)
        axes[0, 0].set_title('Top 10 - Probabilidad de Ser Campeón', fontsize=12, fontweight='bold')
    
    # 2. Probabilidades de subcampeón
    runners = sorted(results['runner_up'].items(), key=lambda x: x[1], reverse=True)[:10]
    if runners:
        teams_r = [t[0] for t in runners]
        probs_r = [(t[1]/total_sims)*100 for t in runners]
        
        axes[0, 1].barh(teams_r, probs_r, color='silver', edgecolor='black')
        axes[0, 1].set_xlabel('Probabilidad (%)', fontsize=11)
        axes[0, 1].set_title('Top 10 - Probabilidad de Ser Subcampeón', fontsize=12, fontweight='bold')
        axes[0, 1].invert_yaxis()
        
        for i, (team, prob) in enumerate(zip(teams_r, probs_r)):
            axes[0, 1].text(prob + 0.5, i, f'{prob:.1f}%', va='center', fontsize=9)
    else:
        axes[0, 1].text(0.5, 0.5, 'Sin datos suficientes', ha='center', va='center', transform=axes[0, 1].transAxes)
        axes[0, 1].set_title('Top 10 - Probabilidad de Ser Subcampeón', fontsize=12, fontweight='bold')
    
    # 3. Probabilidades de semifinales
    semis = sorted(results['semifinalists'].items(), key=lambda x: x[1], reverse=True)[:10]
    if semis:
        teams_s = [t[0] for t in semis]
        probs_s = [(t[1]/total_sims)*100 for t in semis]
        
        axes[1, 0].barh(teams_s, probs_s, color='lightblue', edgecolor='black')
        axes[1, 0].set_xlabel('Probabilidad (%)', fontsize=11)
        axes[1, 0].set_title('Top 10 - Probabilidad de Llegar a Semifinales', fontsize=12, fontweight='bold')
        axes[1, 0].invert_yaxis()
        
        for i, (team, prob) in enumerate(zip(teams_s, probs_s)):
            axes[1, 0].text(prob + 0.5, i, f'{prob:.1f}%', va='center', fontsize=9)
    else:
        axes[1, 0].text(0.5, 0.5, 'Sin datos suficientes', ha='center', va='center', transform=axes[1, 0].transAxes)
        axes[1, 0].set_title('Top 10 - Probabilidad de Llegar a Semifinales', fontsize=12, fontweight='bold')
    
    # 4. Distribución de campeones (torta)
    if champions:
        top_5_champions = dict(champions[:5])
        other_prob = sum([v/total_sims*100 for k, v in champions[5:]])
        top_5_champions['Otros'] = other_prob
        
        axes[1, 1].pie(top_5_champions.values(), labels=top_5_champions.keys(), 
                       autopct='%1.1f%%', startangle=90)
        axes[1, 1].set_title('Distribución de Campeones (Top 5 + Otros)', fontsize=12, fontweight='bold')
    else:
        axes[1, 1].text(0.5, 0.5, 'Sin datos suficientes', ha='center', va='center', transform=axes[1, 1].transAxes)
        axes[1, 1].set_title('Distribución de Campeones', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('figures/monte_carlo_results.png', dpi=300, bbox_inches='tight')
    plt.show()

def export_results_to_excel(results, num_simulations):
    """Exporta los resultados a un archivo Excel"""
    
    total_sims = sum(results['champion'].values())
    if total_sims == 0:
        print("⚠️ No hay datos suficientes para exportar a Excel.")
        return
    
    probabilities = {}
    for stage in results:
        probabilities[stage] = {}
        for team, count in results[stage].items():
            probabilities[stage][team] = (count / total_sims) * 100
    
    # Crear DataFrame para cada etapa
    with pd.ExcelWriter('results/simulation_results.xlsx', engine='openpyxl') as writer:
        for stage, probs in probabilities.items():
            if probs:  # Solo si hay datos
                df = pd.DataFrame(list(probs.items()), columns=['Equipo', 'Probabilidad (%)'])
                df = df.sort_values('Probabilidad (%)', ascending=False)
                df.index = range(1, len(df) + 1)
                
                # Nombre amigable para la hoja
                sheet_name = {
                    'champion': 'Campeones',
                    'runner_up': 'Subcampeones',
                    'third_place': 'Tercer_Lugar',
                    'semifinalists': 'Semifinales',
                    'quarterfinalists': 'Cuartos_Final',
                    'round_of_16': 'Octavos_Final',
                    'group_stage_exit': 'Fase_Grupos'
                }.get(stage, stage)
                
                df.to_excel(writer, sheet_name=sheet_name[:31])  # Excel limita a 31 caracteres
        
        # Hoja de resumen
        summary_data = {
            'Métrica': ['Número de Simulaciones', 'Simulaciones Exitosas', 'Total Equipos', 'Fecha Simulación'],
            'Valor': [num_simulations, total_sims, len(probabilities.get('champion', {})), 
                     pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')]
        }
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Resumen', index=False)
    
    print("✅ Resultados exportados a 'results/simulation_results.xlsx'")

def main():
    """Función principal"""
    
    print("=" * 70)
    print("   SIMULACIÓN MONTE CARLO - MUNDIAL FIFA 2026")
    print("   Investigación Operativa II - UCB Cochabamba")
    print("=" * 70)
    print("\n🔧 Inicializando sistema...")
    
    # Configurar directorios
    setup_directories()
    
    # Cargar equipos
    print("\n📊 Cargando datos de selecciones nacionales...")
    csv_path = 'data/world_cup_teams.csv'
    
    # Verificar que existe el archivo CSV
    if not os.path.exists(csv_path):
        print(f"❌ Error: No se encuentra el archivo '{csv_path}'")
        print("   Asegúrate de que el archivo existe en la ubicación correcta.")
        return
    
    teams = Team.load_from_csv(csv_path)
    print(f"✅ {len(teams)} selecciones cargadas correctamente")
    
    # Mostrar equipos principales
    print("\n🏆 Top 10 selecciones según ranking FIFA:")
    for i, team in enumerate(sorted(teams, key=lambda t: t.ranking)[:10], 1):
        print(f"   {i:2d}. {team.name:20s} - Ranking: {team.ranking:3d} | Elo: {team.elo_rating}")
    
    # Configurar simulación
    print("\n" + "=" * 70)
    num_simulations = 2000  # Número de simulaciones (puede ajustarse)
    print(f"🎲 Configurando simulación Monte Carlo con {num_simulations} iteraciones...")
    
    # Ejecutar simulación
    print("\n🚀 Iniciando simulación...")
    print("   (Este proceso puede tomar varios minutos dependiendo del número de simulaciones)\n")
    
    start_time = time.time()
    
    simulation = MonteCarloSimulation(teams, num_simulations)
    results = simulation.run_simulations()
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    print(f"\n⏱️  Tiempo total de simulación: {elapsed_time:.2f} segundos")
    
    # Mostrar resultados
    simulation.print_summary()
    
    # Generar gráficos
    print("\n📈 Generando gráficos estadísticos...")
    plot_results(results, num_simulations)
    
    # Exportar resultados
    print("\n💾 Exportando resultados a Excel...")
    export_results_to_excel(results, num_simulations)
    
    # Guardar resultados detallados en CSV
    total_sims = sum(results['champion'].values())
    if total_sims > 0:
        print("\n📝 Guardando resultados detallados...")
        probabilities = {}
        for stage in results:
            probabilities[stage] = {}
            for team, count in results[stage].items():
                probabilities[stage][team] = (count / total_sims) * 100
        
        # Guardar top 10 campeones
        top_champions = sorted(probabilities['champion'].items(), key=lambda x: x[1], reverse=True)[:20]
        if top_champions:
            df_top = pd.DataFrame(top_champions, columns=['Equipo', 'Probabilidad_Campeon (%)'])
            df_top.to_csv('results/top_champions.csv', index=False)
    
    print("\n" + "=" * 70)
    print("✅ SIMULACIÓN COMPLETADA EXITOSAMENTE")
    print("=" * 70)
    print("\n📁 Archivos generados:")
    if os.path.exists('figures/monte_carlo_results.png'):
        print("   - figures/monte_carlo_results.png (Gráficos de resultados)")
    if os.path.exists('results/simulation_results.xlsx'):
        print("   - results/simulation_results.xlsx (Resultados completos en Excel)")
    if os.path.exists('results/top_champions.csv'):
        print("   - results/top_champions.csv (Top 20 probabilidades de campeón)")
    print("\n" + "=" * 70)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Simulación interrumpida por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error durante la ejecución: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)