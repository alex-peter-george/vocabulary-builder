import { Component, OnInit } from '@angular/core';
import { DataService } from './api';
import { FormControl, FormsModule } from '@angular/forms';
import { HttpErrorResponse } from '@angular/common/http';
import { environment } from 'src/environment';
import { plainToClass } from 'class-transformer';
import { Observable } from 'rxjs';
import { startWith, debounceTime, switchMap } from 'rxjs/operators';
import { forkJoin } from 'rxjs';
import { HttpClient } from '@angular/common/http';


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
  public photoUrl = '';
  public userDefinition: string = '';
  
  public averageDicScore: number = 0.0;
  public averageOpenAiScore: number = 0.0;
  public sumDicScore: number = 0;
  public sumOpenAiScore: number = 0;
  runsCount: number = 0;
  
  constructor(private dataService: DataService, private http: HttpClient) {
    this.selectedExpression = new Expression();
    this.quizStartTime = new Date();
  }

  ngOnInit() {
    this.callerror = '';
  }

  renderPhoto(){
    let count = 1;
    let url = `https://api.unsplash.com/photos/random?query=${this.selectedExpression.stem}&count=${count}&client_id=${environment.UNSPLASH_ACCESS_KEY}`;
    this.http.get(url).subscribe((response: any) => {
      this.photoUrl = response[0].urls.small;
    });
  } 

  async selectWordRandomly() {
    console.log(`Running environment is set to ${environment.ENVIRONMENT}`)

    this.callerror = '';
    this.showSearchResults = false;
    this.showWordDefs = false;
    this.userDefinition = '';
    
    this.dataService.fetchRandomWord().then(
      (data) => {
        const jsonStr = JSON.stringify(data);
        try{
          const jsonObj = JSON.parse(jsonStr);
          this.showSearchResults = true;
          this.selectedExpression.word = jsonObj['word'];
          this.selectedExpression.stem = jsonObj['stem'];
          //this.expressions.push({word: jsonObj['word'],stem: jsonObj['stem'],dicscore:0.10,openaiscore:0.10, dictionaryDef:'', openAiDef: '', userDef:''});
        }
        catch{
          this.showSearchResults = false;
        }
      },
      (error) => {
        if (error instanceof HttpErrorResponse)
          this.callerror = `Failed selectWordRandomly():${this.dataService.serializeError(error)}`;
        else
          this.callerror = `Failed selectWordRandomly():${error.message}`;
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

    this.averageDicScore = 0.0;
    this.averageOpenAiScore = 0;

    this.sumDicScore = 0;
    this.sumOpenAiScore = 0;
    this.runsCount = 0;

    this.expressions = [];
    this.quizStartTime = new Date();
    
    // this.dataService.fetchRandomWord().then(
    //   (data) => {
    //     const jsonStr = JSON.stringify(data);
    //     try{
    //       const jsonObj = JSON.parse(jsonStr);
    //       this.showSearchResults = true;
    //       this.selectedExpression.word = jsonObj['word'];
    //       this.selectedExpression.stem = jsonObj['stem'];
    //     }
    //     catch{
    //       this.showSearchResults = false;
    //     }
    //   },
    //   (error) => {
    //     if (error instanceof HttpErrorResponse)
    //       this.callerror = this.dataService.serializeError(error);
    //     else
    //       this.callerror = error.message;
    //   }
    // );
  
  }

  submitUserAnswer(userAnswer:string) {
    console.log(`Running environment is set to ${environment.ENVIRONMENT}`)

    var query_str = this.searchControl.value;
    this.callerror = '';
    this.showSearchResults = true;
    this.showWordDefs = true;
    this.freeDictionaryDef = '<Wait for data to load...>';
    this.openAiDef = '<Wait for data to load...>';
    
    this.dataService.postDictionaryDef(this.selectedExpression.word, environment.DICTIONARYDEFURL).then(
        response => {
          console.log('[OK][Angular client] Data received:', response);
          this.freeDictionaryDef = response["meanings"];
        },
        error => {
          console.log('[Bad][Angular client] Error received:', error);
          if (error instanceof HttpErrorResponse)
            this.callerror = `Failed submitUserAnswer.dataService.postDictionaryDef(...):${this.dataService.serializeError(error)}`;
          else
            this.callerror = `Failed submitUserAnswer.dataService.postDictionaryDef(...):${error.message}`;
        }
      );
    
    this.dataService.postOpenAiDef(this.selectedExpression.word, environment.OPENAIDEFURL).then(
        response => {
          console.log('[OK][Angular client] Data received:', response);
          this.openAiDef = response;
          this.calculateSimilarityScores(userAnswer);
        },
        error => {
          console.log('[Bad][Angular client] Error received:', error);
          if (error instanceof HttpErrorResponse)
            this.callerror = `Failed submitUserAnswer.dataService.postOpenAiDef(...):${this.dataService.serializeError(error)}`;
          else
            this.callerror = `Failed submitUserAnswer.dataService.postOpenAiDef(...):${error.message}`;
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
    
    this.renderPhoto();
  }
  
  calculateSimilarityScores(userAnswer: string){
    // Calculate the similarity scores
    let dictScore = 0;
    let openaiScore = 0;  
    this.dataService.postResultGetScores(userAnswer, this.freeDictionaryDef, this.openAiDef).then(
      response => {
        console.log('[OK][Angular client] Data received:', response);
        //this.openAiDef = response;
        dictScore = response['dicSimilarity'];
        openaiScore = response['openAiSimilarity'];
        // Update the list of expressions tab;e  
        this.expressions.push({word: this.selectedExpression.word,stem: this.selectedExpression.stem,dicscore:dictScore,openaiscore:openaiScore, dictionaryDef:'', openAiDef: '', userDef:''});
        // calculate average scores
        this.runsCount = this.runsCount + 1;
        this.sumDicScore = this.sumDicScore + dictScore;
        this.sumOpenAiScore = this.sumOpenAiScore + openaiScore;
        this.averageDicScore = this.sumDicScore / this.runsCount;
        this.averageOpenAiScore = this.sumOpenAiScore / this.runsCount;

      },
      error => {
        console.log('[Bad][Angular client] Error received:', error);
        if (error instanceof HttpErrorResponse)
          this.callerror = `Failed calculateSimilarityScores(...):${this.dataService.serializeError(error)}`;
        else
          this.callerror = `Failed calculateSimilarityScores(...):${error.message}`;
      }
    );  
  }
  
}


