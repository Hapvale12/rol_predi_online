import json
import pandas as pd

def cargar_feriados_locales(ruta_json='feriados.json'):
    """Carga todos los feriados desde el archivo JSON local a un diccionario."""
    feriados_totales = {}
    try:
        with open(ruta_json, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for year, holidays in data.items():
                for holiday in holidays:
                    feriados_totales[holiday['fecha']] = holiday['nombre']
        print("✅ Feriados locales cargados exitosamente.")
        return feriados_totales
    except FileNotFoundError:
        print(f"⚠️ Alerta: No se encontró el archivo '{ruta_json}'. No se podrá verificar feriados.")
    except json.JSONDecodeError:
        print(f"❌ ERROR: El archivo '{ruta_json}' tiene un formato incorrecto.")
    except Exception as e:
        print(f"❌ ERROR inesperado al cargar feriados: {e}")
    return {}

def obtener_feriados_semana(fecha_inicio, fecha_fin, ruta_json='feriados.json'):
    """Identifica y reporta los feriados que caen en la semana seleccionada."""
    print("\nConsultando feriados para la semana seleccionada...")
    feriados_cargados = cargar_feriados_locales(ruta_json)
    feriados_en_semana = set()
    if feriados_cargados:
        fechas_semana = pd.date_range(start=fecha_inicio, end=fecha_fin)
        for fecha in fechas_semana:
            fecha_str = fecha.strftime('%Y-%m-%d')
            if fecha_str in feriados_cargados:
                nombre_feriado = feriados_cargados[fecha_str]
                dia_semana = fecha.strftime('%A').capitalize()
                print(f"✨ ¡ATENCIÓN! El día {dia_semana} {fecha.day} es feriado: {nombre_feriado}")
                feriados_en_semana.add(fecha.date())
    return feriados_en_semana