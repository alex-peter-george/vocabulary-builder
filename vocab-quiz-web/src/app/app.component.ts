import { Component, OnInit } from '@angular/core';
import { DataService } from './api';
import { FormControl } from '@angular/forms';
import { HttpErrorResponse } from '@angular/common/http';
import { environment } from 'src/environment';
import { plainToClass } from 'class-transformer';
import { Observable } from 'rxjs';
import { startWith, debounceTime, switchMap } from 'rxjs/operators';


class Expression {
  
  word: string;
	stem: string;
  dicscore: number;
  openaiscore: number;
  constructor(){
    this.word = '';
    this.stem = '';
    this.dicscore = 0.10;
    this.openaiscore = 0.10;
    // this.dictionaryDef = '';
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
  public selectedExpression: Expression = new Expression();
  public callerror: string = '';
  public showSearchResults: boolean = false;
  public showWordDefs: boolean = false;
  public currentEnv: string = environment.ENVIRONMENT;
  
  constructor(private dataService: DataService) {
  }

  ngOnInit() {
    this.callerror = '';
    // this.dataService.fetchWordsList().then(
    //   (data) => {
    //     this.expressions = data;
    //   },
    //   (error) => {
    //     this.callerror = error;
    //     console.error(error);
    //   }
    // );
  }

  async selectWordRandomly() {
    console.log(`Running environment is set to ${environment.ENVIRONMENT}`)

    // var query_str = this.searchControl.value;
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
          // this.dataService.postDictionaryDef(jsonObj['word'], environment.DICTIONARYDEF).then(
          //   response => {
          //     this.selectedExpression.dictionaryDef = JSON.parse(response)["meanings"];
          //   },
          //   error => {
          //     this.selectedExpression.dictionaryDef = "Error reading Free Dictionary API";
          //   }
          // );

          this.expressions.push({word: jsonObj['word'],stem: jsonObj['stem'],dicscore:0.10,openaiscore:0.10});
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

  async submitUserAnswer() {
    console.log(`Running environment is set to ${environment.ENVIRONMENT}`)

    var query_str = this.searchControl.value;
    this.callerror = '';
    this.showSearchResults = false;
    this.showWordDefs = true;
    
    // this.dataService.postDictionaryDef(jsonObj['word'], environment.DICTIONARYDEF).then(
    //     response => {
    //       this.selectedExpression.dictionaryDef = JSON.parse(response)["meanings"];
    //     },
    //     error => {
    //       if (error instanceof HttpErrorResponse)
    //         this.callerror = this.dataService.serializeError(error);
    //       else
    //         this.callerror = error.message;
    //     }
    //   );

    
  
  }
  
}


