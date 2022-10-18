import requests
import lxml
import lxml.html


class teleco(object):
    def __init__(self):
        self.response = None
        self.ddds = []
        self.get_ddds()
    def get_ddds(self):
        url = 'https://www.teleco.com.br/num_cel.asp'
        try:
            response = requests.get(url, timeout=10)
            x = lxml.html.fromstring(response.content)
            e = x.xpath('//table[@class="boxazul"]')
            ddds = e[0].xpath('./tr')[2].xpath('./td/span/select/option')
            for ddd in ddds:
                if ddds.index(ddd) not in (0, 1):
                    self.ddds.append({'ddd': ddd.attrib['value'].strip(), 'faixas': []})
            return True
        except Exception as err:
            print(f'teleco.get_ddds exception - {err}')
        return False
    def has_faixa_to_ddd(self, ddd):
        for item_ddd in self.ddds:
            if item_ddd['ddd'] == ddd:
                if len(item_ddd['faixas'])>0:
                    return item_ddd
        return False
    def get_carrier_by_number(self, number, ddd=None):
        if len(number) == 11:
            ddd = number[0:2]
            number = number[2:]
        elif len(number) != 9 and ddd == None:
            return False
        temp_faixas = self.has_faixa_to_ddd(ddd=ddd)
        if temp_faixas == False:
            avoid = self.get_response_carrier_by_ddd(ddd=ddd)
            if avoid == True:
                return self.get_carrier_by_number(number=number, ddd=ddd)
        else:
            temp_prefix = int(number[0:5])
            for option in temp_faixas['faixas']:
                for option_carrier in option['faixas']:
                    if '-' in option_carrier:
                        max_carrier = int(option_carrier.split('-')[0].strip())
                        min_carrier = int(option_carrier.split('-')[1].strip())
                    else:
                        max_carrier = int(option_carrier.strip())
                        min_carrier = int(option_carrier.strip())
                    if (temp_prefix >= max_carrier) and (temp_prefix <= min_carrier):
                        return option
            return temp_faixas
    def add_faixas_ddd(self, ddd, resposta):
        for item_ddd in self.ddds:
            if item_ddd['ddd'] == ddd:
                item_ddd.update({'faixas': resposta})
                return item_ddd
        return False
    def get_response_carrier_by_ddd(self, ddd):
        url = f'https://www.teleco.com.br/carrega_numeros_operadora.asp?dd={ddd}'
        headers = {
            'Accept-Encoding': 'gzip, deflate, br'
        }
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                xbody = lxml.html.fromstring(response.content)
                resposta = []
                elem_faixas = xbody.xpath('//table/tr')
                if elem_faixas:
                    for row in elem_faixas:
                        if elem_faixas.index(row) > 0:
                            carrier = ''
                            faixas = []
                            row_td = row.xpath('./td')
                            if len(row_td) == 2:
                                elem_carrier = row_td[0].xpath('./img')
                                if elem_carrier:
                                    temp_carrier = elem_carrier[0].attrib['src'].strip()
                                    temp_carrier = temp_carrier[temp_carrier.rindex('/')+1:]
                                    carrier = temp_carrier[0:temp_carrier.index('.')]
                                elem_faixas_td = row_td[1].text_content().strip()
                                for faixa in elem_faixas_td.split('\n'):
                                    if len(faixa.strip())>0:
                                        faixas.append(faixa.strip())
                                temp = {'carrier': carrier.strip(), 'faixas': faixas}
                                resposta.append(temp)
                    self.add_faixas_ddd(ddd, resposta)
                    return True
        except Exception as err:
            print(f'teleco.get_response exception - {err}')
        return False


#####

#>>> ca = teleco()
#>>> ca.get_carrier_by_number('19999583622')

##{'carrier': 'Vivo', 'faixas': ['97100-97199', '99600-99999']}
