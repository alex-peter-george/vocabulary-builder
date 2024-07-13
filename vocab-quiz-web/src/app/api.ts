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
  
  postDictionaryDef(word: string, url: string) : Promise<any> {
    // return new Promise((response,error) => 
    //   this.http.post(url, {"expression" : word}).subscribe(
    //     response => {
    //       console.log('[OK][Data Service] Data received:', response);
    //       return JSON.stringify(response);
    //     },
    //     error => {
    //       console.error('[Bad][Data Service] Error received:', error);
    //       return '{"error" : "' + error + '"}';
    //     }
    //   ));
    return this.http.post(url, {"expression" : word}).toPromise();
  }

  postOpenAiDef(word: string, url: string) : Promise<any> {
    // return new Promise((response,error) => 
    //   this.http.post(url, {"expression" : word}).subscribe(
    //     response => {
    //       console.log('[OK][Data Service] Data received:', response);
    //       return JSON.stringify(response);
    //     },
    //     error => {
    //       console.error('[Bad][Data Service] Error received:', error);
    //       return '{"error" : "' + error + '"}';
    //     }
    //   ));
    return this.http.post(url, {"expression" : word}).toPromise();
  }

  postResultGetScores(user_answer: string, dict_definition: string, openai_definition: string) : Promise<any> {
    // this.http.post(this.simScoresUrl, {"user_definition" : user_answer, "dictionary_definition" : dict_definition, "openai_definition" : openai_definition}).subscribe(
    //   response => {
    //     console.log('Data sent successfully:', response);
    //     return JSON.stringify(response);
    //   },
    //   error => {
    //     console.error('Error sending data:', error);
    //     return "error";
    //   }
    // );
    return this.http.post(this.simScoresUrl, {"user_definition" : user_answer, "dictionary_definition" : dict_definition, "openai_definition" : openai_definition}).toPromise();
  }

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




