'''
Created on Jun 9, 2011

@author: Brian
'''
from utils.geocode import get_country

def filter_by_countries(app_users, countries):
    users = set()
    for user in app_users:
        country = get_country(address=user.location, sensor="false")
        if country in countries:
            users.add(user)             
    return users

def filter_by_gender(app_users, gender):
    users = set()
    for user in app_users:
        if user.gender == gender:
            users.add(user)             
    return users

def isOfAge(birthDate, age=18):
    import datetime
    endDate = datetime.date.today()
    years = endDate.year - birthDate.year
    if years == age:
        return (birthDate.month < endDate.month or 
                (birthDate.month == endDate.month and birthDate.day < endDate.day))         
    return years > age
