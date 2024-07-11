import { Component, OnInit } from '@angular/core';
import { DataService } from './api';
import { FormControl } from '@angular/forms';
import { HttpErrorResponse } from '@angular/common/http';
import { environment } from 'src/environment';
import { plainToClass } from 'class-transformer';
import { Observable } from 'rxjs';
import { startWith, debounceTime, switchMap } from 'rxjs/operators';
import { forkJoin } from 'rxjs';


class Expression {
  word: string;
	stem: string;
  dicscore: number;
  openaiscore: number;
  dictionaryDef: string;
  openAiDef: string;
  userDef: string;
  constructor(){
    this.word = '';
    this.stem = '';
    this.dicscore = 0.10;
    this.openaiscore = 0.10;
    this.dictionaryDef = '';
    this.openAiDef = '';
    this.userDef = '';
  }
}

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})

export class AppComponent implements OnInit {
  title = "List of selected words and expressions";
  public expressions: Expression[] = [];
  searchControl = new FormControl('');
  public selectedExpression: Expression;
  public callerror: string = '';
  public showSearchResults: boolean = false;
  public showWordDefs: boolean = false;
  public currentEnv: string = environment.ENVIRONMENT;
  public freeDictionaryDef: string = '';
  public openAiDef: string = '';
  public quizStartTime: Date;
  
  constructor(private dataService: DataService) {
    this.selectedExpression = new Expression();
    this.quizStartTime = new Date();
  }

  ngOnInit() {
    this.callerror = '';

  }

  async selectWordRandomly() {
    console.log(`Running environment is set to ${environment.ENVIRONMENT}`)

    this.callerror = '';
    this.showSearchResults = false;
    this.showWordDefs = false;
    
    this.dataService.fetchRandomWord().then(
      (data) => {
        const jsonStr = JSON.stringify(data);
        try{
          const jsonObj = JSON.parse(jsonStr);
          this.showSearchResults = true;
          this.selectedExpression.word = jsonObj['word'];
          this.selectedExpression.stem = jsonObj['stem'];
          
          this.expressions.push({word: jsonObj['word'],stem: jsonObj['stem'],dicscore:0.10,openaiscore:0.10, dictionaryDef:'', openAiDef: '', userDef:''});
        }
        catch{
          this.showSearchResults = false;
        }
      },
      (error) => {
        if (error instanceof HttpErrorResponse)
          this.callerror = this.dataService.serializeError(error);
        else
          this.callerror = error.message;
      }
    );
    
  }

  async startNewQuiz() {
    console.log(`Running environment is set to ${environment.ENVIRONMENT}`)

    var query_str = this.searchControl.value;
    this.callerror = '';
    this.showSearchResults = false;
    this.showWordDefs = false;
    this.quizStartTime = new Date();
    
    this.dataService.fetchRandomWord().then(
      (data) => {
        const jsonStr = JSON.stringify(data);
        try{
          const jsonObj = JSON.parse(jsonStr);
          this.showSearchResults = true;
          this.selectedExpression.word = jsonObj['word'];
          this.selectedExpression.stem = jsonObj['stem'];
        }
        catch{
          this.showSearchResults = false;
        }
      },
      (error) => {
        if (error instanceof HttpErrorResponse)
          this.callerror = this.dataService.serializeError(error);
        else
          this.callerror = error.message;
      }
    );
  
  }

  submitUserAnswer() {
    console.log(`Running environment is set to ${environment.ENVIRONMENT}`)

    var query_str = this.searchControl.value;
    this.callerror = '';
    this.showSearchResults = false;
    this.showWordDefs = true;
    this.freeDictionaryDef = '<Wait for data to load...>';
    this.openAiDef = '<Wait for data to load...>';
    
    this.dataService.postDictionaryDef(this.selectedExpression.word, environment.DICTIONARYDEFURL).then(
        response => {
          this.freeDictionaryDef = response["meanings"];
        },
        error => {
          if (error instanceof HttpErrorResponse)
            this.callerror = this.dataService.serializeError(error);
          else
            this.callerror = error.message;
        }
      );
    
    this.dataService.postOpenAiDef(this.selectedExpression.word, environment.OPENAIDEFURL).then(
        response => {
          console.log('[OK][Angular client] Data received:', response);
          this.openAiDef = response;
        },
        error => {
          console.log('[Bad][Angular client] Error received:', error);
          if (error instanceof HttpErrorResponse)
            this.callerror = this.dataService.serializeError(error);
          else
            this.callerror = error.message;
        }
      );
    
    // let requestFreeDict = this.dataService.postDictionaryDef(this.selectedExpression.word, environment.DICTIONARYDEFURL);
    // let requestOpenAi = this.dataService.postOpenAiDef(this.selectedExpression.word, environment.OPENAIDEFURL);
  
    // forkJoin([requestFreeDict, requestOpenAi]).subscribe(([requestFreeDict, requestOpenAi]) => {
      
    //   if (requestFreeDict.includes("meanings")){
    //     console.log(requestFreeDict);
    //     this.freeDictionaryDef = JSON.parse(requestFreeDict)["meanings"];
    //   }
    //   else {
    //     console.log(requestOpenAi);
    //     this.openAiDef = requestOpenAi;
    //   }
    // });
  }
  
}


