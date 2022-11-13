import ally


a = ally.Ally()
qt = a.timesales('TSLA', '2022-09-29', '2022-10-01', dataframe=False)
accts = a.get_accounts()
