{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "917f64cd",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "✅ Histórico de 3 años generado en data/bogota_market_share_history.csv\n"
     ]
    }
   ],
   "source": [
    "import pandas as pd\n",
    "import numpy as np\n",
    "from datetime import datetime, timedelta\n",
    "\n",
    "def generate_market_war_data():\n",
    "    localidades = ['Suba', 'Kennedy', 'Engativá', 'Bosa', 'Usaquén', 'Chapinero']\n",
    "    competidores = ['Margarita', 'Super Ricas', 'Marcas_Propias_D1', 'Pringles']\n",
    "    canales = ['Tradicional', 'Moderno']\n",
    "    \n",
    "    data = []\n",
    "    start_date = datetime(2023, 1, 1)\n",
    "    \n",
    "    for i in range(1185): # Aprox 3 años y algo\n",
    "        current_date = start_date + timedelta(days=i)\n",
    "        is_quincena = current_date.day in [15, 30]\n",
    "        \n",
    "        for loc in localidades:\n",
    "            for canal in canales:\n",
    "                # Simular trancón en Bogotá (Afecta logística)\n",
    "                delay_index = np.random.randint(0, 60) \n",
    "                osa_impact = 1.0 if delay_index < 30 else 0.85\n",
    "                \n",
    "                for comp in competidores:\n",
    "                    # Lógica de Share Base\n",
    "                    base_sales = 1000 if comp == 'Margarita' else 400\n",
    "                    if comp == 'Marcas_Propias_D1' and canal == 'Moderno':\n",
    "                        base_sales += 200 # D1 fuerte en moderno\n",
    "                    \n",
    "                    # Impacto de Promoción Sintética (Ataque de competencia)\n",
    "                    promo_hit = 0.9 if (comp == 'Margarita' and np.random.random() < 0.1) else 1.0\n",
    "                    \n",
    "                    sales = base_sales * osa_impact * promo_hit\n",
    "                    if is_quincena: sales *= 1.3 # Pico de quincena en Bogotá\n",
    "                    \n",
    "                    data.append([current_date, loc, canal, comp, round(sales, 2), delay_index])\n",
    "\n",
    "    df = pd.DataFrame(data, columns=['Fecha', 'Localidad', 'Canal', 'Competidor', 'Ventas_Valor', 'Retraso_Logistico_Min'])\n",
    "    df.to_csv('data/bogota_market_share_history.csv', index=False)\n",
    "    print(\"✅ Histórico de 3 años generado en data/bogota_market_share_history.csv\")\n",
    "\n",
    "if __name__ == \"__main__\":\n",
    "    generate_market_war_data()"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.14.2"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
