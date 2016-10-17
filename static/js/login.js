/* This example will only work in the latest browsers */
const initApp = () => {
  const registryToken = "3895d6d5-0656-42ae-9d7d-fc0daf4af801";

  const login = () => {
    Rosefire.signIn(registryToken, (err, rfUser) => {
      if (err) {
        return;
      }
      window.location.replace('/login?token=' + rfUser.token);
    });
  };
  const loginButton = document.getElementById('login');
  if (loginButton) {
    loginButton.onclick = login;
  }
}

window.onload = initApp;

