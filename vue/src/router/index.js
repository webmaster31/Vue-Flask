import Vue from 'vue'
import VueRouter from 'vue-router'
import LoginPage from "../views/Login.vue";

Vue.use(VueRouter);

// 
// THIS WILL CHECK IF USER IS LOGGED IN OR NOT
// 

function checkValidity() {
  const token = localStorage.getItem('token');
  const userInfo = localStorage.getItem('userInfo');
  if (token && userInfo)
    return true;
  return false;
}

const routes = [
  {
    path: "/login",
    name: "Login",
    component: LoginPage,
    beforeEnter(to, from, next) {
      if (checkValidity()) {
        next(from.path)
      } else {
        next();
      }
    }
  },
  {
    path: "/session/login/:token/:uidb",
    name: "Session Login",
    component: () => import(/* webpackChunkName: "Confirmation" */ "../views/Confirmation.vue"),
    beforeEnter(to, from, next) {
      if (checkValidity()) {
        next(from.path)
      } else {
        next();
      }
    }
  },
  {
    path: "/session/reset-password/:token/:uidb",
    name: "Session Password Reset",
    component: () => import(/* webpackChunkName: "Session Password Reset" */ "../views/NewPassword.vue"),
    beforeEnter(to, from, next) {
      if (checkValidity()) {
        next(from.path)
      } else {
        next();
      }
    }
  },
  {
    path: "/signup",
    name: "Signup",
    component: () => import(/* webpackChunkName: "Signup" */ "../views/Signup.vue"),
    beforeEnter(to, from, next) {
      if (checkValidity()) {
        next(from.path)
      } else {
        next();
      }
    }
  },
  {
    path: "/reset-password",
    name: "Reset Password",
    component: () => import(/* webpackChunkName: "Reset-Password" */ "../views/ResetPassword.vue"),
    beforeEnter(to, from, next) {
      if (checkValidity()) {
        next(from.path)
      } else {
        next();
      }
    }
  },
  {
    path: "*",
    component: () => import(/* webpackChunkName: "Main" */ "../layout/Main.vue"),
  },
  {
    path: "",
    component: () => import(/* webpackChunkName: "Main" */ "../layout/Main.vue"), 
    meta: { requiresAuth: true },
    beforeEnter(to, from, next) {
      const isValid = checkValidity();
      if (isValid) {
        next();
      } else {
        next('/login');
      }
    },
    children: [
      {
        path: '/dashboard',
        name: 'Dashboard',
        meta: { requiresAuth: true },
        component: () => import( /* webpackChunkName: "Dashboard" */ "../views/Dashboard.vue"),
      },
    ]
  }
];

const router = new VueRouter({
  mode: 'history',
  routes
});

export default router;
