from codigo_de_ejecucion import *
import streamlit as st
from streamlit_echarts import st_echarts

#CONFIGURACION DE LA PÁGINA
st.set_page_config(
     page_title = 'Risk Score Analyzer by Miguel',
     page_icon = 'foto perfil miguel.png',
     layout = 'wide')

# SIDEBAR #####################################################################################
import os
image_path = os.path.join(os.path.dirname(__file__), 'High-Risk-scaled.jpg')

with st.sidebar:
    st.image(image_path, width=400)
    st.markdown(
        '''
        <div style="margin-top:30px">
            Esta aplicación predice la pérdida esperada en un préstamo individual. Se basa en el cálculo de 
            
 EL = PD * P * EAD * LGD
 
 donde:
 
* "EL" es la pérdida esperada.
* "P" es la cantidad de prestamo solicitada.
* "PD" es la probabilidad de default.
* "EAD" es el valor de exposición en default.
* "LGD" es la tasa de recuperación en default.
 
Cada modelo se entrenó con datos históricos y se validó para asegurar la predicción.
        </div>
        ''',
        unsafe_allow_html=True
    )
################################################################################################

st.title('RISK SCORE ANALYZER')

with st.expander("Definir los parámetros del préstamo individual", expanded=False):

    #INPUTS DE LA APLICACION
    col1,col2,col3 = st.columns(3) # ----------------------------------------------------------
    with col1:
        principal = st.number_input('Importe Solicitado', 500, 50000, help= 'Cantidad solicitada de préstamo') 
    with col2:
        finalidad = st.selectbox('Finalidad Préstamo',  ['debt_consolidation', 'small_business', 'car','major_purchase',
                                                         'credit_card','other','medical', 'home_improvement', 'house','moving',
                                                          'vacation', 'wedding','renewable_energy','educational'], help= 'Finalidad del préstamo')
    
    col1,col2,col3,col4,col5,col6,col7 = st.columns([1,1,2,1,1,1,1]) # -------------------------------------------------------
   
    with col1:
        num_cuotas = st.selectbox('Número Cuotas', ['36 months','60 months'], help='número de cuotas iniciales del préstamo')

    with col3:
        ingresos = st.number_input('Ingresos anuales', 20000, 300000, help='Ingresos anuales')
        

    with col5:
        ingresos_verificados =st.selectbox('Opciones ingresos',['Not Verified','Verified', 'Source Verified'], help='si los ingresos declarados por el cliente han sido verificados')

    with col7:
        antigüedad_empleo =st.selectbox('Antiguedad empleo', ['< 1 year','1 year','2 years','3 years','4 years','5 years',
                                         '6 years','7 years','8 years','9 years','10+ years'], help='antigüedad en años en su puesto de trabajo')

    
    col1,col2,col3,col4,col5,col6,col7, = st.columns(7) # -------------------------------------------------------

    with col1:
        rating = st.selectbox('Rating', index=1, options= ['A', 'B', 'C', 'D', 'E', 'F', 'G'], help='rating según agencias')

    with col3:
        dti = st.number_input('DTI', 0.01, 100.0, format='%.2f', help='(Debt-to-Income ratio) es el ratio entre el total de deuda del cliente y sus ingresos mensuales, excluyendo hipotecas')

    with col5:
        num_lineas_credito = st.number_input('Líneas de credito', 0, help='número de líneas de crédito abiertas del cliente')

    with col7:
        porc_uso_revolving = st.number_input('% límite revolving', 0, 100, help='% uso de límite revolving')

    
    col1,col2,col3,col4,col5,col6,col7, = st.columns(7) # --------------------------------------------------------

    with col1:
        tipo_interes = st.number_input('Tipo interés', 5, help= 'Tasa de interes en %')

    with col3:
        imp_cuota = st.number_input('Importe cuota', 1, help='Importe mensual cuota del prestamo')

    with col5:
        num_derogatorios = st.number_input('Derogatorios', 0, help='Numero de Derogatorios')

    with col7:
        vivienda = st.selectbox('Titularidad de vivienda',['NONE','MORTGAGE', 'RENT', 'OWN', 'ANY'], help="Tipo de titularidad de la vivienda")



#CALCULAR

#Crear el registro
registro = pd.DataFrame({'ingresos_verificados':ingresos_verificados,
                         'vivienda':vivienda,
                         'finalidad':finalidad,
                         'num_cuotas':num_cuotas,
                         'antigüedad_empleo':antigüedad_empleo,
                         'rating':rating,
                         'ingresos':ingresos,
                         'dti':dti,
                         'num_lineas_credito':num_lineas_credito,
                         'porc_uso_revolving':porc_uso_revolving,
                         'principal':principal,
                         'tipo_interes':tipo_interes,
                         'imp_cuota':imp_cuota,
                         'num_derogatorios':num_derogatorios}
                        ,index=[0])




#CALCULAR RIESGO
if st.button('CALCULAR RIESGO'):

    #Ejecutar el scoring
    EL = ejecutar_modelos(registro)

    #Calcular los kpis
    kpi_pd = int(EL.pd * 100)
    kpi_ead = int(EL.ead * 100)
    kpi_lgd = int(EL.lgd * 100)
    kpi_el = int(EL.principal * EL.pd * EL.ead * EL.lgd)

    pd_options = {
            "tooltip": {"formatter": "{a} <br/>{b} : {c}%"},
            "series": [
                {
                    "name": "PD",
                    "type": "gauge",
                    "axisLine": {
                        "lineStyle": {
                            "width": 10,
                        },
                    },
                    "progress": {"show": "true", "width": 10},
                    "detail": {"valueAnimation": "true", "formatter": "{value}"},
                    "data": [{"value": kpi_pd, "name": "PD"}],
                }
            ],
        }

    #Velocimetro para ead
    ead_options = {
            "tooltip": {"formatter": "{a} <br/>{b} : {c}%"},
            "series": [
                {
                    "name": "EAD",
                    "type": "gauge",
                    "axisLine": {
                        "lineStyle": {
                            "width": 10,
                        },
                    },
                    "progress": {"show": "true", "width": 10},
                    "detail": {"valueAnimation": "true", "formatter": "{value}"},
                    "data": [{"value": kpi_ead, "name": "EAD"}],
                }
            ],
        }

    #Velocimetro para lgd
    lgd_options = {
            "tooltip": {"formatter": "{a} <br/>{b} : {c}%"},
            "series": [
                {
                    "name": "LGD",
                    "type": "gauge",
                    "axisLine": {
                        "lineStyle": {
                            "width": 10,
                        },
                    },
                    "progress": {"show": "true", "width": 10,},
                    "detail": {"valueAnimation": "true", "formatter": "{value}"},
                    "data": [{"value": kpi_lgd, "name": "LGD"}],
                }
            ],
        }
    #Representarlos en la app
    col1,col2,col3 = st.columns(3)
    with col1:
        st_echarts(options=pd_options, width="110%", key=0)
    with col2:
        st_echarts(options=ead_options, width="110%", key=1)
    with col3:
        st_echarts(options=lgd_options, width="110%", key=2)

    #Prescripcion
    col1,col2,col3,col4 = st.columns(4)
    with col1:
        st.write('La pérdida esperada es de (Soles):')
        st.metric(label="PÉRDIDA ESPERADA", value = kpi_el)
    with col2:
        st.write('Se recomienda un extratipo de (Soles):')
        # por simplicidad aqui se coloca manualmente una comision adicional
        st.metric(label="COMISIÓN A APLICAR", value = kpi_el*3) 

else:
    st.write('DEFINE LOS PARÁMETROS DEL PRÉSTAMO Y HAZ CLICK EN CALCULAR RIESGO')
