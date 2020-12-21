import pandas as pd
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.arima_model import ARIMA

def arimaRun(list_tpm,list_date) :

    d = {'date':list_date, 'tpm':list_tpm}
    series = pd.Series(index=list_date,data=list_tpm)

    diff_1=series.diff(periods=1).iloc[1:]
    model = ARIMA(series, order=(0,1,1))
    model_fit = model.fit(trend='nc',full_output=True, disp=1)
    fore = model_fit.forecast(steps=1)
    series.to_csv('/root/Downloads/ar.csv')
    result = [fore[0][0], fore[2][0][1]]
    return result
