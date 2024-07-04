import { Component, OnInit } from '@angular/core';
import { DataService } from './api';
import { FormControl } from '@angular/forms';
import { HttpErrorResponse } from '@angular/common/http';
import { environment } from 'src/environment';
import { plainToClass } from 'class-transformer';
import { Observable } from 'rxjs';
import { startWith, debounceTime, switchMap } from 'rxjs/operators';


interface ArbDocument {
  RunAnalysis: number;
	DocumentId: string;
	DocumentName: string;
	DocumentFileName: string;
	DocumentURL: string;
  ExtractedContent: string;
  IsHandwritten: string;
  ConfidenceLevels: string;
  LastAnalyseDate: string;
}

export class ArbSearch {
  constructor(
    answer: string,
    similarity: string,
    documentTitle: string,
    documentID: string,
    documentURL: string,
  )
  {
    this.Answer = answer;
    this.Similarity = similarity;
    this.DocumentTitle = documentTitle;
    this.DocumentID = documentID;
    this.DocumentURL = documentURL;
  }
  Answer: string;
  Similarity: string;
  DocumentTitle: string;
  DocumentID: string;
  DocumentURL: string;
}

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {
  title = "ARB Documents";
  public documents: ArbDocument[] = [];
  searchControl = new FormControl('');
  public searchResult: ArbSearch[] = [];
  public callerror: string = '';
  public showSearchResults: boolean = false;
  public currentEnv: string = '';
  
  constructor(private dataService: DataService) {
  }

  ngOnInit() {
    this.callerror = '';
    if (environment.production == true) {
      this.currentEnv = "Production";
      this.dataService.fetchDocList().then(
        (data) => {
          this.documents = data;
        },
        (error) => {
          this.callerror = error;
          console.error(error);
        }
      );
    }  
    else {
      this.currentEnv = "Testing";
      this.dataService.fetchTestDocList().subscribe(
        (data) => {
          this.documents = data;
          console.log(data);
        },
        (error) => {
          this.callerror = error;
          console.error(error);
        }
      );
    }
  }

  trackItem(item: ArbDocument) {
    return item ? item.DocumentId : undefined;
  }

  async searchArbDocs() {
    console.log(`Production environment is set to ${environment.production}`)

    var query_str = this.searchControl.value;
    this.callerror = '';
    this.showSearchResults = false;
    if (environment.production == true) {
      this.dataService.fetchSearch(query_str).subscribe(
        (data) => {
          const jsonStr = JSON.stringify(data);
          const jsonObj = JSON.parse(jsonStr);
          this.searchResult = [];
          if (jsonObj.length > 0){
            this.showSearchResults = true;
            jsonObj.forEach((item: { Answer: string; Similarity: string; DocumentTitle: string; DocumentID: string; DocumentURL: string; }) => (
              this.searchResult.push(new ArbSearch(item.Answer,item.Similarity,item.DocumentTitle,item.DocumentID,item.DocumentURL)))
            );
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
    else
    {
      this.dataService.fetchTestSearch(query_str).subscribe(
        (data) => {
          const jsonStr = JSON.stringify(data);
          console.log(jsonStr);
          const jsonObj = JSON.parse(jsonStr);
          // jsonObj.map((item: { answer: string; confidence: string; documentTitle: string; documentID: string; documentURL: string; }) => (new ArbSearch(item.answer,item.confidence,item.documentTitle,item.documentID,item.documentURL)))
          
          this.searchResult = [];
          if (jsonObj.length > 0){
            this.showSearchResults = true;
            jsonObj.forEach((item: { Answer: string; Similarity: string; DocumentTitle: string; DocumentID: string; DocumentURL: string; }) => (
              this.searchResult.push(new ArbSearch(item.Answer,item.Similarity,item.DocumentTitle,item.DocumentID,item.DocumentURL)))
            );
          }
        },
        (error) => {
          if (error instanceof HttpErrorResponse)
            this.callerror = this.dataService.serializeError(error);
          else
            this.callerror = error.message;
          console.error(error);
        }
      )
    }
  }
}


