export const googleAuthSettings = {
  clientId: process.env.VUE_APP_GOOGLE_CLIENT_ID,
  scope: 'profile email',
  prompt: 'select_account'
}

export const facebookAuthSettings = {
  appId: process.env.VUE_APP_FACEBOOK_APP_ID,
  cookie: true,
  xfbml: true,
  version: 'v2.8'
}
