import requests
from json import JSONDecodeError


__api_key__ = None

__phone_status__ = {'daw':'dad'}


def set(api_key:str) -> bool:
    global __api_key__
    if __api_key__ is None:
        __api_key__ = api_key
        return True
    else:
        return False
def get() -> str:
    global __api_key__
    if __api_key__ is not None:
        return __api_key__
    else:
        set(input('Please enter your API-KEY'))
        return __api_key__
def __get__(url:str) -> str:
    try:
        response =  requests.get(url)
        if __check__(response.text):
            return response
    except ConnectionResetError:
        return 'ERROR'
    except:
        return 'ERROR'

def __check__(response:str) -> bool:
    if response.__contains__('BAD_KEY'):
        set(input('Please enter valid key!'))
        return False
    if response.__contains__('ERROR_SQL'):
        print('Error on server!')
        return False
    if response.__contains__('BAD_ACTION'):
        print('Bad action!')
        return False
    if response.__contains__('BAD_SERVICE'):
        print('Bad service!')
        return False       
    if response.__contains__('NO_ACTIVATION'):
        print('This id not registered!')
        return False
    return True
# decorators!
def cost(func):
    def wrapper(service:str):
        old_bal = balance()
        result = func(service)
        new_bal = balance()
        print('Cost: ' + str(round(old_bal-new_bal, 2)))
        return result
    return wrapper
def onCode(func):
    def wrapper():
        global __phone_status__
        codes = ()
        while codes == ():
            for i in __phone_status__.items():
                id = i[1]
                number = i[0]
                response = __get__(f'https://smshub.org/stubs/handler_api.php?\
                                    api_key={get()}&\
                                    action=getStatus&\
                                    id={id}').text
                if response.__contains__('STATUS_OK'):
                    if setStatus(id, 1):
                        code = response.split(':')[1]
                        codes = (number,code)
                elif response.__contains__('STATUS_CANCEL'):
                    del __phone_status__[number]
        result = func(codes)
        return result
    return wrapper

def setStatus(id:str, status:str) -> bool:
    response = __get__(f'https://smshub.org/stubs/handler_api.php?\
                        api_key={get()}&\
                        action=setStatus&\
                        status={status}&\
                        id={id}').text
    if response.__contains__('ACCESS_ACTIVATION'):
        return True
    if response.__contains__('ACCESS_CANCEL'):
        return True
    return False

def balance() -> float:
    response = __get__(f'https://smshub.org/stubs/handler_api.php?\
                            api_key={get()}&\
                            action=getBalance').text
    return float(response.split(':')[1])
@cost
def phone(service:str) -> str:
    global __phone_status__
    response = __get__(f'https://smshub.org/stubs/handler_api.php?\
                        api_key={get()}&\
                        action=getNumber&\
                        service={service}&\
                        operator=any&\
                        country=0').text
    if response.__contains__('NO_NUMBERS'):
        print('No avaible numbers!')
        return None
    if response.__contains__('NO_BALANCE'):
        print('F$ck$ng sh$t! NO balance!')
        return None
    if response.__contains__('WRONG_SERVICE'):
        print('No valid service!')
        return None
    elements = response.split(':')  
    id = elements[1]
    number = elements[2]
    __phone_status__[number] = id  
    return number
