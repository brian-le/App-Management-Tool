'''
Created on May 24, 2011

@author: Brian
'''
def pretty_print(timezone):
    #s=(UTC+05:45) Kathmandu
    offset = float(timezone.offset)
    if offset == 0:
        return "(UTC) " + timezone.description 
    
    s = "(UTC"     
    hour = int(offset)
    minute = int((abs(offset) - abs(hour))*60)
    
    if hour >= 0:
        hour = '+' + str(hour)
    minute = str(minute)
    
    if len(minute)==1:
        minute = '0' + minute
    
    hour = str(hour)
    minute = str(minute)
    s = s + hour + ":" + minute + ") " + timezone.description
    
    return s 
