from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from datetime import datetime
from selenium.webdriver.chrome.options import Options
import time

# --- Variáveis de Configuração ---
URL_SISTEMA = "https://selimp25.sflip.online/"
USUARIO = "CPLU367502"
SENHA = "85630415"

# --- GERAÇÃO DA RESPOSTA DINÂMICA ---
DATA_HOJE = datetime.now().strftime("%d/%m/%Y")
TEXTO_RESPOSTA = (
    f"Prezada(o) cidadão, sobre sua solicitação, informamos que a equipe executou o serviço "
    f"{DATA_HOJE}. Para mais Informações de Nossos serviços consulte o o site www.cplu.com.br, Agradecemos o contato, Equipe CPLU"
)

# --- Elementos da Página (Localizadores) ---
CAMPO_LOGIN_XPATH = "//input[@type='text']"
CAMPO_SENHA_XPATH = "//input[@type='password']"
BOTAO_ENTRAR_XPATH = "//button[text()='Entrar']"
MENU_SAC_156_XPATH = "//a[contains(., 'SAC 156')]"
OPCAO_HOME_INTERNO_XPATH = "//div[@id='menu-SAC156']/ul//a[text()='Home']"
CARD_EXECUTADO_XPATH = "//div[contains(text(), 'Executado') and not(contains(text(), 'Não')) and not(contains(text(), 'Confirma'))]"
ICONE_ACAO_PRIMEIRO_SERVICO_XPATH = "//table//tbody/tr[1]/td[1]//*[1]"

# Localizadores do DETALHE/MODAL
BOTAO_ABRIR_MODAL_ID = "btn_publicar"
CAMPO_OBSERVACAO_ID = "txt_observacao_publicar"
BOTAO_CONFIRMAR_MODAL_XPATH = "//div[@id='modal-finalizar']//button[contains(text(), 'Confirmar')] | //button[contains(text(), 'Publicar')]"
BOTAO_OK_SUCESSO_XPATH = "//button[text()='OK'] | //button[contains(text(), 'OK')]"


def digitar_lentamente(elemento, texto, delay=0.01):
    for caractere in texto:
        elemento.send_keys(caractere)
        time.sleep(delay)


def navegar_para_lista(driver, wait):
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
    print("Acessando lista de serviços 'Executados'...")
    card_executado = wait.until(EC.element_to_be_clickable((By.XPATH, CARD_EXECUTADO_XPATH)))
    card_executado.click()
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//table")))
    print("Navegação inicial concluída. Iniciando loop de processamento.")


def processar_servico_executado(driver, wait):
    try:
        icone_acao = wait.until(EC.element_to_be_clickable((By.XPATH, ICONE_ACAO_PRIMEIRO_SERVICO_XPATH)))
        icone_acao.click()
    except StaleElementReferenceException:
        print(">> Referência obsoleta. Tentando localizar e clicar novamente.")
        icone_acao = wait.until(EC.element_to_be_clickable((By.XPATH, ICONE_ACAO_PRIMEIRO_SERVICO_XPATH)))
        icone_acao.click()

    print(">> Abrindo detalhes do serviço...")
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)
    botao_abrir_modal = wait.until(EC.element_to_be_clickable((By.ID, BOTAO_ABRIR_MODAL_ID)))
    botao_abrir_modal.click()
    print(">> Modal de Publicação aberto.")
    time.sleep(3)
    campo_observacao = wait.until(EC.presence_of_element_located((By.ID, CAMPO_OBSERVACAO_ID)))
    campo_observacao.clear()
    digitar_lentamente(campo_observacao, TEXTO_RESPOSTA)
    print(">> Texto inserido.")
    botao_confirmar = wait.until(EC.element_to_be_clickable((By.XPATH, BOTAO_CONFIRMAR_MODAL_XPATH)))
    botao_confirmar.click()
    print(">> Serviço submetido e finalizado.")
    botao_ok = wait.until(EC.element_to_be_clickable((By.XPATH, BOTAO_OK_SUCESSO_XPATH)))
    botao_ok.click()
    print(">> Mensagem de sucesso fechada. Retornando à lista.")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, ICONE_ACAO_PRIMEIRO_SERVICO_XPATH)))
    time.sleep(1)


def iniciar_automacao():
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920,1080")
    print("Navegador configurado em MODO VISÍVEL.")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    wait = WebDriverWait(driver, 15)

    try:
        navegar_para_lista(driver, wait)
        servicos_processados = 0
        print("\n" + "="*50)
        print("INICIANDO PROCURA E PROCESSAMENTO DE SERVIÇOS...")
        print("="*50 + "\n")

        while True:
            try:
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, ICONE_ACAO_PRIMEIRO_SERVICO_XPATH))
                )
                print(f"--- Processando Serviço #{servicos_processados + 1} ---")
                processar_servico_executado(driver, wait)
                servicos_processados += 1
            except TimeoutException:
                print("\n" + "*"*50)
                if servicos_processados == 0:
                    print("✔ STATUS: A LISTA DE SERVIÇOS 'EXECUTADOS' ESTÁ VAZIA.")
                else:
                    print("✔ SUCESSO! A LISTA FOI ZERADA NESTE CICLO.")
                    print(f"Total de serviços processados: {servicos_processados}")
                print("*"*50 + "\n")
                break
            except Exception as e:
                print(f"\n[ERRO FATAL NO PROCESSO] Falha ao processar o serviço atual. Erro: {e}")
                break
    except Exception as e:
        print(f"\n--- ERRO CRÍTICO NO CICLO DE EXECUÇÃO ---")
        print(f"Ocorreu um erro na navegação inicial ou setup: {e}")
    finally:
        if 'driver' in locals() and driver:
            driver.quit()


if __name__ == "__main__":
    try:
        while True:
            print(f"\n{'#'*60}")
            print(f"INICIANDO NOVO CICLO DE AUTOMAÇÃO (Horário: {datetime.now().strftime('%H:%M:%S')})")
            print(f"{'#'*60}")
            iniciar_automacao()
            PAUSA_SEGUNDOS = 120
            print(f"--- Ciclo concluído. Pausando por {PAUSA_SEGUNDOS} segundos (2 minutos). ---")
            time.sleep(PAUSA_SEGUNDOS)
    except KeyboardInterrupt:
        print("\n\nAutomação interrompida pelo usuário. Finalizando.")
