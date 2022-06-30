include "globals.mzn";
include "chuffed.mzn";

% --------------------------- CONFIGs ---------------------------

% Check the following boxes in the solver configuration:
  % SOLVER  -> Chuffed;
  % SOLVING -> Free search;
  % OUTPUT  -> Output solving statistics;

% Toy case
%w_c = [3,2,2,3,4];
%h_c = [3,4,8,9,12];
%n = 5;
%w = 9;

% w_c=[34, 13, 13, 10, 10, 6, 6, 25, 25, 21, 16, 16, 21, 21, 5, 5, 4, 4, 6, 12, 12, 23, 7, 7, 2, 2, 6, 6, 14, 14, 16, 16, 14, 14, 14, 3, 3, 11, 11, 6, 6, 33, 12, 12, 16, 12, 12, 4, 4, 3, 3, 6, 6, 6, 6, 5, 5, 3, 3, 9, 6, 6, 2, 2, 8, 8, 10, 3, 3, 3, 3, 2, 2];
% h_c=[6, 3, 5, 12, 12, 7, 15, 7, 15, 12, 7, 5, 3, 5, 7, 5, 1, 10, 13, 13, 9, 6, 3, 5, 1, 10, 6, 5, 7, 6, 3, 5, 6, 5, 13, 2, 7, 2, 7, 7, 6, 14, 4, 3, 18, 3, 18, 4, 3, 1, 2, 9, 9, 1, 2, 7, 18, 9, 9, 18, 5, 2, 12, 9, 3, 9, 9, 5, 2, 18, 7, 3, 9];
% n=73;
% w=60;


% n=22;
% w=26;
% w_c=[3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4];
% h_c=[3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 16, 17, 19, 3, 4, 5, 7, 8, 11, 14];

% -------------------------- VARIABLES --------------------------

int: w;                               % Width of the silicon plate
int: n;                               % Number of components

array[1..n] of int: w_c;              % Width of components
array[1..n] of int: h_c;              % Height of components
array[1..n] of var int: area;         % Areas of components

int: max_h = sum(h_c[1..n]);              % Height of the silicon plate 

array[1..n] of var 1..max(w,max_h): x;    % x dimensions of components
array[1..n] of var 1..max(w,max_h): y;    % y dimensions of components

% Variable to minimize
var int: h = max([y[i] + h_c[i] | i in 1..n])-1; 

% ------------------------- CONSTRAINTS -------------------------

% CONSTRAINT 1.1
% Areas definition constraint
constraint 
  forall (i in 1..n)
    (area[i] = w_c[i] * h_c[i]);

% CONSTRAINT 1.2
% Each circuits inside the silicon plate
constraint 
  forall (i in 1..n) 
    (x[i] <= w - w_c[i] + 1);

% CONSTRAINT 1.3
% No overlap 
constraint 
  diffn (x[1..n], y[1..n], w_c[1..n], h_c[1..n]) :: domain;


constraint cumulative(y[1..n], h_c[1..n], w_c[1..n], w) :: domain;
constraint cumulative(x[1..n], w_c[1..n], h_c[1..n], h) :: domain;
var int: empty_space=w*h-sum(area);
constraint empty_space>=0;


% ----------------- SIMMETRY BREAKING CONSTRAINTS ----------------- 

% CONSTRAINT 2.1
% Break simmetry constraint: pos[i,1] <= w-pos[i,1]-dim[i,1]+1
var int: i_max = arg_max(area); 

constraint 
  2 * x[i_max] <= w - w_c[i_max] + 2;
constraint 
  2 * y[i_max] <= h - h_c[i_max] + 2;
  
%%FIXME 
% constraint 
%  forall(i,j in 1..n where i!=j) ((x[i]=x[j] /\ w_c[i]=w_c[j])->   (area[i]>area[j]->y[i]<y[j]));
% constraint 
%  forall(i,j in 1..n where i!=j) ((y[i]=y[j] /\ h_c[i]=h_c[j])->   (area[i]>area[j]-> x[i]<x[j]));

% constraint
%   forall (i,j in 1..n)
%   ((((x[i] + w_c[i] == x[j]) \/ (x[j] + w_c[j] == x[i])) /\ area[i] >= area[j]) -> x[i] < x[j]);
  
% constraint
%   forall (i,j in 1..n)
%   ((((y[i] + h_c[i] == y[j]) \/ (y[j] + h_c[j] == y[i])) /\ area[i] >= area[j]) -> y[i] < y[j]);

%constraint 
%  2 * x[i_max] <= w - w_c[i_max] + 1;
%constraint 
%  2 * y[i_max] <= h - h_c[i_max] + 1;

% ------------------------------ SEARCH ------------------------------
ann: search_ann = priority_search(area, 
      [int_search([y[i],x[i]], input_order, indomain_min) | i in 1..n],largest, complete);

solve :: search_ann minimize h;

output
 ["[[\(w), \(h)],\n"] ++ 
 ["[\(w_c[i]), \(h_c[i]), \(x[i]), \(y[i])],\n" | i in 1..n-1] ++
 ["[\(w_c[n]), \(h_c[n]), \(x[n]), \(y[n])]]"]