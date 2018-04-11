//  Copyright 2013 Google Inc. All Rights Reserved.
//
//  Licensed under the Apache License, Version 2.0 (the "License");
//  you may not use this file except in compliance with the License.
//  You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
//  Unless required by applicable law or agreed to in writing, software
//  distributed under the License is distributed on an "AS IS" BASIS,
//  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//  See the License for the specific language governing permissions and
//  limitations under the License.

#include <stdio.h>
#include <string.h>
#include <math.h>
#include <malloc.h>

const long long max_size = 2000;         // max length of strings
const long long N = 40;                  // number of closest words that will be shown
const long long max_w = 50;              // max length of vocabulary entries

int main(int argc, char **argv) {
  FILE *f;
  char file_name[max_size];
  float len;
  long long words, size, a, b;
  char ch;
  float *M;
  char *vocab;
  if (argc < 2) {
    printf("Usage: ./readbin <FILE>\nwhere FILE contains word projections in the BINARY FORMAT\n");
    return 0;
  }
  strcpy(file_name, argv[1]);
  f = fopen(file_name, "rb");
  if (f == NULL) {
    printf("Input file not found\n");
    return -1;
  }
  fscanf(f, "%lld", &words);
  fscanf(f, "%lld", &size);
  printf("%lld %lld\n",words,size);
  vocab = (char *)malloc(max_w * sizeof(char));
  M = (float *)malloc((long long)size * sizeof(float));
  if (M == NULL) {
    printf("Cannot allocate memory\n");
    return -1;
  }
  for (b = 0; b < words; b++) {
    fscanf(f, "%s%c", vocab, &ch);
    printf("%s ", vocab);

    for (a = 0; a < size; a++) fread(&M[a], sizeof(float), 1, f);
    len = 0;
    for (a = 0; a < size; a++) len += M[a] * M[a];
    len = sqrt(len);
    for (a = 0; a < size; a++) M[a] /= len;

    for (a = 0; a < size-1; a++){ printf("%f ",M[a]); }
    printf("%f\n",M[a]);
  }
  fclose(f);

  return 0;
}
