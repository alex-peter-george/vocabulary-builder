// import * as data from '../assets/data';
import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import * as Papa from 'papaparse';

@Injectable({
  providedIn: 'root'
})

export class DataService {
  private wordsTestUrl = 'http://localhost:7071/api/expression_list';
  // private searchTestUrl = "http://localhost:7071/api/search_by_query"
  
  private wordsUrl = 'https://arb-ai-search-api.azurewebsites.net/api/arb_docs_list?code=LCQGNiSKpsntUfFGOHVHpwk4HjR8xuxt1BgvDUDQjyL0AzFur4Lh5Q%3D%3D';
  // private searchUrl = 'https://arb-ai-search-api.azurewebsites.net/api/search_by_query?code=ZTnVI5mWprrPXW-AN8xgl3yiPhbz9zPjT3cJEeqz6vliAzFuo_4tUA%3D%3D';
    
  constructor(private http: HttpClient) {}

  // fetchTestWordsList(): Observable<any> {
  //   return this.http.get(this.wordsTestUrl);
  // }

  async fetchTestWordsList() {
    const r = await fetch(this.wordsTestUrl);
    return await r.json();
  }

  async fetchWordsList() {
    const r = await fetch(this.wordsUrl);
    return await r.json();
  }

  // fetchTestSearch(query_string: any) : Observable<any> {
  //   const body = { query: query_string };
  //   return this.http.post(this.searchTestUrl, body);
  // }

  // fetchSearch(query_string: any): Observable<any> {
  //   const body = { query: query_string };
  //   console.log(`Production Search URL is ${this.searchUrl}`)
  //   return this.http.post(this.searchUrl, body);
  // }

  serializeError(error: HttpErrorResponse): string {
    const serializedError = {
      // Extract the properties you need
      message: error.message,
      status: error.status,
      error: error.error
    };
    return JSON.stringify(serializedError);
  }
}




