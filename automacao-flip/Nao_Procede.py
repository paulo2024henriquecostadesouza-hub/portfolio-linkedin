from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from datetime import datetime
import time

# --- Variáveis de Configuração ---
URL_SISTEMA = "https://selimp25.sflip.online"
USUARIO = "CPLU367502"
SENHA = "85630415"
DATA_HOJE = datetime.now().strftime("%d/%m/%Y")

# --- Mapeamento de Respostas ---
RESPOSTA_PROGRAMACAO = (
    "Prezada(o) cidadão, sobre sua solicitação, informamos que este serviço segue uma programação de trabalho, "
    "consulte no site https://cplu.com.br . Agradecemos o contato. Equipe CPLU."
)
SERVICOS_PROGRAMACAO = [
    "Lavagem especial de equipamentos públicos",
    "Varrição manual de vias e logradouros públicos",
    "Limpeza e desobstrução de bueiros, bocas de lobo e bocas de leão",
    "Equipe de Mutirão de Zeladoria de Vias e Logradouros Públicos"
]

FULL_CUSTOM_RESPONSE_REMOVED = (
    "Prezada(o) cidadão, sobre sua solicitação, vistoriamos o local, e não havia material "
    "para remoção. Por gentileza abra uma nova solicitação com o endereço "
    "exato/ponto de referência. Agradecemos o contato Equipe CPLU."
)
SERVICOS_FULL_CUSTOM_REMOVED = [
    "Coleta e transporte de entulho e grandes objetos depositados irregularmente nas vias, logradouros e áreas públicas",
    "Remoção de animais mortos de proprietários não identificados em vias e logradouros públicos"
]

RESPOSTA_PADRAO_FINAL = "Prezada(o) cidadão, sobre sua solicitação, vistoriamos o local, e trata-se de um serviço escalonado, com datas programadas à critérios técnicos de execução. consulte o site https://cplu.com.br para mais informações.Agradecemos o contato Equipe CPLU."

# --- Localizadores ---
CAMPO_LOGIN_XPATH = "//input[@type='text']"
CAMPO_SENHA_XPATH = "//input[@type='password']"
BOTAO_ENTRAR_XPATH = "//button[text()='Entrar']"
MENU_SAC_156_XPATH = "//a[contains(., 'SAC 156')]"
OPCAO_HOME_INTERNO_XPATH = "//div[@id='menu-SAC156']/ul//a[text()='Home']"
CARD_NAO_PROCEDE_XPATH = "//div[contains(text(), 'Não Procede')]"
ICONE_ACAO_PRIMEIRO_SERVICO_XPATH = "//table//tbody/tr[1]/td[1]//*[1]"
CAMPO_TIPO_SERVICO_XPATH = "//span[contains(text(), 'Serviço:')]/following-sibling::span[1] | //label[contains(text(), 'Serviço:')]/following-sibling::span[1] | //label[contains(text(), 'Serviço:')][last()]"
BOTAO_ABRIR_MODAL_ID = "btn_publicar"
CAMPO_OBSERVACAO_ID = "txt_observacao_publicar"
BOTAO_OK_SUCESSO_XPATH = "//button[text()='OK'] | //button[contains(text(), 'OK')]"


def digitar_lentamente(elemento, texto, delay=0.01):
    for caractere in texto:
        elemento.send_keys(caractere)
        time.sleep(delay)


def navegar_para_lista_nao_procede(driver, wait):
    print("Iniciando navegação inicial...")
    driver.get(URL_SISTEMA)
    campo_login = wait.until(EC.presence_of_element_located((By.XPATH, CAMPO_LOGIN_XPATH)))
    campo_login.send_keys(USUARIO)
    campo_senha = driver.find_element(By.XPATH, CAMPO_SENHA_XPATH)
    campo_senha.send_keys(SENHA)
    botao_entrar = driver.find_element(By.XPATH, BOTAO_ENTRAR_XPATH)
    botao_entrar.click()
    time.sleep(2)
    menu_sac_156 = wait.until(EC.element_to_be_clickable((By.XPATH, MENU_SAC_156_XPATH)))
    menu_sac_156.click()
    time.sleep(1)
    opcao_home = wait.until(EC.element_to_be_clickable((By.XPATH, OPCAO_HOME_INTERNO_XPATH)))
    opcao_home.click()
    print("Acessando lista de serviços 'Não Procede'...")
    card_nao_procede = wait.until(EC.element_to_be_clickable((By.XPATH, CARD_NAO_PROCEDE_XPATH)))
    card_nao_procede.click()
    print("Lista de serviços 'Não Procede' carregada.")


def recarregar_lista_nao_procede(driver, wait):
    print("Recarregando a lista 'Não Procede'...")
    try:
        card_nao_procede = wait.until(EC.element_to_be_clickable((By.XPATH, CARD_NAO_PROCEDE_XPATH)))
        card_nao_procede.click()
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//table")))
        print("✔ Lista recarregada.")
        return True
    except Exception as e:
        print(f"✖ ERRO ao recarregar a lista 'Não Procede': {e}")
        return False


def gerar_resposta_customizada(tipo_servico):
    if tipo_servico in SERVICOS_PROGRAMACAO:
        print("Mapeamento: PROGRAMAÇÃO")
        return RESPOSTA_PROGRAMACAO
    if tipo_servico in SERVICOS_FULL_CUSTOM_REMOVED:
        print("Mapeamento: CUSTOMIZADA (Não havia material)")
        return FULL_CUSTOM_RESPONSE_REMOVED
    print("Mapeamento: PADRÃO DE ERRO")
    return RESPOSTA_PADRAO_FINAL


def processar_proximo_servico(driver, wait):
    try:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, ICONE_ACAO_PRIMEIRO_SERVICO_XPATH)))
    except TimeoutException:
        print("--- CONDIÇÃO DE PARADA ---")
        print("⚠️ A lista 'Não Procede' está vazia.")
        return False

    try:
        print("\n[FLUXO] Processando o próximo serviço...")
        icone_acao = driver.find_element(By.XPATH, ICONE_ACAO_PRIMEIRO_SERVICO_XPATH)
        icone_acao.click()
        print("✔ Detalhes do serviço abertos.")
    except Exception as e:
        print(f"✖ ERRO ao clicar no ícone de ação: {e}. Retornando.")
        return False

    tipo_servico = "Serviço Não Mapeado"
    try:
        elemento_tipo_servico = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, CAMPO_TIPO_SERVICO_XPATH))
        )
        texto_capturado = elemento_tipo_servico.text.strip()
        if "Serviço:" in texto_capturado:
            tipo_servico = texto_capturado.split("Serviço:", 1)[-1].strip()
        else:
            tipo_servico = texto_capturado.strip()
        print(f"SERVIÇO CAPTURADO: *{tipo_servico}*")
    except Exception as e:
        print(f"✖ FALHA na captura do serviço. Usando resposta padrão. Erro: {e}")

    resposta_completa = gerar_resposta_customizada(tipo_servico)
    print(f"RESPOSTA GERADA: {resposta_completa[:50]}...")

    print("✔ Realizando rolagem e abrindo o modal de finalização...")
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)

    try:
        botao_abrir_modal = wait.until(EC.element_to_be_clickable((By.ID, BOTAO_ABRIR_MODAL_ID)))
        botao_abrir_modal.click()
        print("✔ Modal de Publicação aberto.")
    except Exception as e:
        print(f"✖ ERRO Crítico: Falha ao clicar no botão de abrir modal. {e}")
        raise

    print("Aguardando 3 segundos para o modal carregar...")
    time.sleep(3)

    try:
        campo_observacao = wait.until(EC.presence_of_element_located((By.ID, CAMPO_OBSERVACAO_ID)))
        campo_observacao.clear()
        digitar_lentamente(campo_observacao, resposta_completa)
        print("✔ Resposta digitada no campo de observação.")
        campo_observacao.send_keys(Keys.TAB)
        time.sleep(0.5)
        driver.switch_to.active_element.send_keys(Keys.TAB)
        time.sleep(0.5)
        driver.switch_to.active_element.send_keys(Keys.ENTER)
        print("✔ Botão de Confirmação Clicado.")
        botao_ok_sucesso = wait.until(EC.element_to_be_clickable((By.XPATH, BOTAO_OK_SUCESSO_XPATH)))
        botao_ok_sucesso.click()
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, ICONE_ACAO_PRIMEIRO_SERVICO_XPATH))
        )
        print("✔ Serviço finalizado com sucesso. Voltando para a tela de lista.")
        recarregar_lista_nao_procede(driver, wait)
    except Exception as e:
        print(f"✖ ERRO Crítico na finalização do modal: {e}")
        try:
            driver.switch_to.active_element.send_keys(Keys.ESCAPE)
        except:
            pass
        raise

    return True


def iniciar_automacao():
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-gpu")
    print("\n" + "#"*60)
    print("INICIANDO Robô de Finalização 'NÃO PROCEDE' (MODO VISÍVEL)")
    print("#"*60 + "\n")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    wait = WebDriverWait(driver, 15)

    try:
        servicos_processados = 0
        navegar_para_lista_nao_procede(driver, wait)
        while True:
            if processar_proximo_servico(driver, wait):
                servicos_processados += 1
                time.sleep(1)
            else:
                print("\n" + "="*50)
                print(f"✔ CICLO CONCLUÍDO. Total processado: {servicos_processados}")
                print("="*50)
                break
    except KeyboardInterrupt:
        print("\n\nAutomação interrompida pelo usuário (CTRL+C). Finalizando.")
    except Exception as e:
        print(f"\n--- ROBÔ PARADO POR ERRO CRÍTICO ---\nOcorreu um erro: {e}")
    finally:
        if 'driver' in locals() and driver:
            print("\nFechando navegador...")
            driver.quit()


if __name__ == "__main__":
    try:
        while True:
            PAUSA_SEGUNDOS = 120
            print(f"\n{'='*70}")
            print(f"INICIANDO NOVO CICLO DE AUTOMAÇÃO (Horário: {datetime.now().strftime('%H:%M:%S')})")
            print(f"{'='*70}")
            iniciar_automacao()
            print(f"\n--- Ciclo concluído. Pausando por {PAUSA_SEGUNDOS} segundos (2 minutos). ---")
            time.sleep(PAUSA_SEGUNDOS)
    except KeyboardInterrupt:
        print("\n\nAutomação interrompida pelo usuário. Finalizando.")
