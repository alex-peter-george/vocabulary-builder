// import * as data from '../assets/data';
import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { environment } from 'src/environment';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import * as Papa from 'papaparse';
import jasmine from 'jasmine';

@Injectable({
  providedIn: 'root'
})

export class DataService {
  private wordsUrl = environment.WORDSURL;
  private randomWordUrl = environment.RANDOMWORDURL;
  private simScoresUrl = environment.SIMSCORESURL;
  private postResponse = '';
      
  constructor(private http: HttpClient) {}

  async fetchWordsList() {
    const r = await fetch(this.wordsUrl);
    return await r.json();
  }

  async fetchRandomWord() {
    const r = await fetch(this.randomWordUrl);
    return await r.json();
  }
  
  async postDictionaryDef(word: string, url: string) : Promise<string> {
    this.http.post(url, {"expression" : word}).subscribe(
      response => {
        console.log('Data sent successfully:', response);
        this.postResponse = JSON.stringify(response);
      },
      error => {
        console.error('Error sending data:', error);
        this.postResponse = "error";
      }
    );
    return this.postResponse;
  }

  async postResultGetScores(word: string, user_answer: string) : Promise<string> {
    this.http.post(this.simScoresUrl, {"expression" : word, "user_answer" : user_answer}).subscribe(
      response => {
        console.log('Data sent successfully:', response);
        this.postResponse = JSON.stringify(response);
      },
      error => {
        console.error('Error sending data:', error);
        this.postResponse = "error";
      }
    );
    return this.postResponse;
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




