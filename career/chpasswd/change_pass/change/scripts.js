const authForm = document.getElementById('auth-form')
const actionsBox = authForm.querySelector('#actions')
const errMsgBox = actionsBox.querySelector('#err-msg')

authForm.addEventListener('submit', handleSubmit)

async function handleSubmit(e) {
  try {
    e.preventDefault()
    actionsBox.classList.add('loading')
    errMsgBox.classList.remove('active')
    errMsgBox.textContent = ''

    const nameInputValue = authForm.querySelector('#httpd_username').value
    const passwordInputValue = authForm.querySelector('#httpd_password').value
    if (!nameInputValue || !passwordInputValue) {
      throw new Error('Заполните все поля')
    }

    const response = await fetch(
      '/login',
      {
        method: 'POST',
        body: new FormData(e.target)
      }
    )
    if (response.status > 399) {
      const data = await response.json()
      throw new Error(data.error)
    }
  } catch (err) {
    errMsgBox.classList.add('active')
    errMsgBox.textContent = err.message
  } finally {
    actionsBox.classList.remove('loading')
  }
}
