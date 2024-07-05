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
  constructor(){
    this.word = '';
    this.stem = '';
  }
}

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})

export class AppComponent implements OnInit {
  title = "List of Words and Expressions";
  public expressions: Expression[] = [];
  searchControl = new FormControl('');
  public selectionResult: Expression = new Expression();
  public callerror: string = '';
  public showSearchResults: boolean = false;
  public currentEnv: string = '';
  
  constructor(private dataService: DataService) {
  }

  ngOnInit() {
    this.callerror = '';
    if (environment.production == true) {
      this.currentEnv = "Production";
      this.dataService.fetchWordsList().then(
        (data) => {
          this.expressions = data;
        },
        (error) => {
          this.callerror = error;
          console.error(error);
        }
      );
    }  
    else {
      this.currentEnv = "Testing";
      this.dataService.fetchTestWordsList().then(
        (data) => {
          this.expressions = data;
          console.log(data);
        },
        (error) => {
          this.callerror = error;
          console.error(error);
        }
      );
    }
  }

  // trackItem(item: Expression) {
  //   return item ? item.DocumentId : undefined;
  // }

  // async searchArbDocs() {
  //   console.log(`Production environment is set to ${environment.production}`)

  //   var query_str = this.searchControl.value;
  //   this.callerror = '';
  //   this.showSearchResults = false;
  //   if (environment.production == true) {
  //     this.dataService.fetchSearch(query_str).subscribe(
  //       (data) => {
  //         const jsonStr = JSON.stringify(data);
  //         const jsonObj = JSON.parse(jsonStr);
  //         this.searchResult = [];
  //         if (jsonObj.length > 0){
  //           this.showSearchResults = true;
  //           jsonObj.forEach((item: { Answer: string; Similarity: string; DocumentTitle: string; DocumentID: string; DocumentURL: string; }) => (
  //             this.searchResult.push(new ArbSearch(item.Answer,item.Similarity,item.DocumentTitle,item.DocumentID,item.DocumentURL)))
  //           );
  //         }
  //       },
  //       (error) => {
  //         if (error instanceof HttpErrorResponse)
  //           this.callerror = this.dataService.serializeError(error);
  //         else
  //           this.callerror = error.message;
  //       }
  //     );
  //   }
  //   else
  //   {
  //     this.dataService.fetchTestSearch(query_str).subscribe(
  //       (data) => {
  //         const jsonStr = JSON.stringify(data);
  //         console.log(jsonStr);
  //         const jsonObj = JSON.parse(jsonStr);
  //         // jsonObj.map((item: { answer: string; confidence: string; documentTitle: string; documentID: string; documentURL: string; }) => (new ArbSearch(item.answer,item.confidence,item.documentTitle,item.documentID,item.documentURL)))
          
  //         this.searchResult = [];
  //         if (jsonObj.length > 0){
  //           this.showSearchResults = true;
  //           jsonObj.forEach((item: { Answer: string; Similarity: string; DocumentTitle: string; DocumentID: string; DocumentURL: string; }) => (
  //             this.searchResult.push(new ArbSearch(item.Answer,item.Similarity,item.DocumentTitle,item.DocumentID,item.DocumentURL)))
  //           );
  //         }
  //       },
  //       (error) => {
  //         if (error instanceof HttpErrorResponse)
  //           this.callerror = this.dataService.serializeError(error);
  //         else
  //           this.callerror = error.message;
  //         console.error(error);
  //       }
  //     )
  //   }
  // }
}


