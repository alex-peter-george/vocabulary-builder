# Azure Vocabulary Builder 

## Concept Design

![vocab-quiz-diagram-1](https://github.com/user-attachments/assets/8053c34c-6902-4ab0-b52c-0ec57917786a)

## Single Page Application with Angular

This project was generated with [Angular CLI](https://github.com/angular/angular-cli) version 16.1.8.

### Development server

Run `ng serve` for a dev server. Navigate to `http://localhost:4200/`. The application will automatically reload if you change any of the source files.

### Code scaffolding

Run `ng generate component component-name` to generate a new component. You can also use `ng generate directive|pipe|service|class|guard|interface|enum|module`.

### Build

Run `ng build` to build the project. The build artifacts will be stored in the `dist/` directory.

### Running unit tests

Run `ng test` to execute the unit tests via [Karma](https://karma-runner.github.io).

### Running end-to-end tests

Run `ng e2e` to execute the end-to-end tests via a platform of your choice. To use this command, you need to first add a package that implements end-to-end testing capabilities.

### Further help

To get more help on the Angular CLI use `ng help` or go check out the [Angular CLI Overview and Command Reference](https://angular.io/cli) page.

### Deploy to Azure Static Web App without Github hooks
Based on the presentation at [Coding Shorts: Deploy to Static Web Apps without GitHub Actions](https://www.youtube.com/watch?v=TkYFT24bZks)

##### Steps

* Create a Static Web App in Azure Portal, with the settings you need
* Open cmd terminal in Angular web folder 
* Install *swa cli tool* with `npm i @azure/static-web-apps-cli -g`
* Run `swa login` to login to Azure, to the proper subscription and tenant; the settings are saved in the newly created .env file
* Configure the tool by running `swa` in the command terminal; check the settings to be correct
* Answer 'no' to request for deploy, then inspect the content of *swa-cli.config.json* file
* Run `swa deploy` in terminal window; upon 'no project found' message, we will need to provide the *deployment token*
* Go to *Azure Portal* and get the managed deployment token from the static web app created there
* Go back to terminal windows and run `swa deploy --deployment-token <managed-token-string>`; swa is deployed in **preview** environment in Azure* 

