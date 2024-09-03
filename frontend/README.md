<div id="top"></div>

# React Frontend Template
This is React frontend template app with tailwind for fast prototyping.

<!-- ABOUT THE PROJECT -->
## About The Project

This is a webapp uses React and Tailwind that will enable fast prototyping without worrying about front-end env setup.

### Built With

* [React](https://reactjs.org/)
* [Tailwind](https://tailwindcss.com/)

<p align="right">(<a href="#top">back to top</a>)</p>


<!-- GETTING STARTED -->
## Getting Started


### From local dev environment

To run the app in development mode, in the project directory, you can run:

```js
npm start
```

Runs the app in the development mode.\
Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

The page will reload if you make edits.\
You will also see any lint errors in the console.

For detail development and deployment, check this create-react-app dcoument at [React-README.md](./React-README.md)


### From Docker

To run the app in docker, without installing all node modules on local environment, run following commands:

```bash
docker-compose build
docker-compose up
```

Once you see following LOG in terminal, the frontend app is ready!

``` sh
react-frontend-template-frontend-1  | Starting the development server...
react-frontend-template-frontend-1  | 
react-frontend-template-frontend-1  | Compiled successfully!
react-frontend-template-frontend-1  | 
react-frontend-template-frontend-1  | You can now view enter-the-matrix in the browser.
react-frontend-template-frontend-1  | 
react-frontend-template-frontend-1  |   Local:            http://localhost:3000
react-frontend-template-frontend-1  |   On Your Network:  http://172.20.0.2:3000
react-frontend-template-frontend-1  | 
react-frontend-template-frontend-1  | Note that the development build is not optimized.
react-frontend-template-frontend-1  | To create a production build, use npm run build.
react-frontend-template-frontend-1  | 
react-frontend-template-frontend-1  | webpack compiled successfully
react-frontend-template-frontend-1  | No issues found.
react-frontend-template-frontend-1  | Compiling...
react-frontend-template-frontend-1  | Compiled successfully!
react-frontend-template-frontend-1  | webpack compiled successfully
react-frontend-template-frontend-1  | No issues found.
```