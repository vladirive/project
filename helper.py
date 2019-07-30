def date_format(value):
    months = ("Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre")
    month  = months[value.month - 1]
    return "{} de {} del {} a las {}:{} ".format(value.day,month,value.year,value.hour,value.minute)
