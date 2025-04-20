# 🩺 Plataforma de Telemedicina

Sistema protótipo desenvolvido para fins acadêmicos, com o objetivo de oferecer uma solução **completa, moderna e superior** às plataformas tradicionais de telemedicina.

---

## 🚀 Funcionalidades atuais

- Login com senha criptografada (segurança com `werkzeug.security`)
- Cadastro de novos usuários com escolha de perfil: `paciente` ou `médico`
- Recuperação de senha (sem necessidade de e-mail)
- Agendamento de consultas com verificação de horário
- Histórico de consultas com filtros (médico, tipo, datas)
- Perfil com edição de dados e exclusão de conta
- Interface amigável e responsiva

---

## 📁 Estrutura


---

## 🛠️ Tecnologias utilizadas

- Python 3.12+
- Flask
- SQLite
- HTML + CSS (vanilla)
- Werkzeug Security

---

## 🧪 Como rodar localmente

```bash
git clone https://github.com/Lucasschwertz/Plataforma-Medicina.git
cd Plataforma-Medicina

python -m venv venv
venv\Scripts\activate      # (no Windows)
pip install -r requirements.txt

python app.py

