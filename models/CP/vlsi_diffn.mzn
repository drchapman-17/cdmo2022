include "globals.mzn";
include "chuffed.mzn";

% solver config:
% Chuffed, free search, output solving statistics

% precision (proportional to w) and number of circuits

% toy case
% dim = [|3,3|2,4|2,8|3,9|4,12|];
% n = 5;
% w = 9;

% case 7
% dim = [|3, 3|3, 4|3, 5|3, 6|3, 7|3, 8|3, 9|5, 4|5, 10|]
% n = 9
% w = 14

% case 14
% dim = [|3, 3|3 ,4|3 ,5|3 ,6|3 ,7|3 ,8|3 ,9|3 ,10|3 ,14|3 ,18|4 ,4|4 ,6|4 ,11|5 ,6|5 ,15|]
% n = 15
% w = 21

% case 30
% dim= [|3, 3|3, 4|3, 5|3, 6|3, 7|3, 8|3, 9|3 ,11|3 ,12|3 ,13|3 ,14|3 ,17|3 ,18|3 ,21|4, 3|4, 4|4, 5|4, 6|4 ,10|4 ,22|4 ,24|5, 3|5, 4|5, 6|5 ,10|5 ,14|12 ,37|]
% n=27
% w=37

% case 31
% dim = [|3, 3|3, 4|3, 5|3, 6|3, 7|3, 8|3, 9|3 ,10|3 ,11|3 ,13|4, 3|4, 5|4, 6|4, 8|4 ,11|4 ,12|4 ,15|4 ,16|24 ,38|]
% n = 19
% w = 38 

% case 34
% dim = [|3 ,11|3 ,13|2, 9|2, 7|3, 9|3, 7|2 ,11|2 ,13|4 ,11|4 ,13|5, 3|2 ,11|2, 2|3 ,11|3, 2|4, 5|4, 6|2 ,12|2, 1|5, 3|5 ,13|4 ,12|4, 1|2, 5|2, 6|]
% n = 25
% w = 15

% case 37
% dim = [|5, 7|5 ,14|8 ,14|8, 4|13 ,21|11, 7|11 ,14|5 ,14|5, 4|3 ,18|3 ,21|11 ,17|11, 4|4, 7|4, 5|7, 6|5 ,18|5, 3|3, 7|3, 5|4 ,18|4, 3|2 ,12|2, 6|5 ,18|5 ,21|3 ,17|3 ,4 |]
% n = 28
% w = 30

% case 38
% dim = [|6 ,18|2 ,12|10, 7|4 ,23|4, 1|7, 7|11, 4|6, 5|2, 7|6 ,11|10 ,19|11 ,5|4, 2|7, 5|4, 2|7 ,12|7 ,13|3, 6|6 ,10|9 ,16|1, 4|4 ,10|6 ,24|9, 9|2, 1|8, 5|3, 5|7 ,25|5 ,21|]
% n = 29
% w = 30

% case 39
% dim = [|9 ,24|9, 8|9 ,11|9 ,17|4 ,24|4, 8|1, 6|1, 5|4 ,17|3, 6|3, 5|12, 5|12 ,13|14 ,14|2 ,14|2, 2|8, 3|8, 9|12 ,14|12, 2|6, 3|6, 9|2, 5|2 ,13|3 ,18|3 ,14|3 ,16|3 ,12|]
% n = 28
% w = 30

% case 40
% n = 73
% w = 60
% dim = [|34, 6|13, 3|13, 5|10 ,12|10 ,12|6, 7|6 ,15|25, 7|25 ,15|21 ,12|16, 7|16, 5|21, 3|21, 5|5, 7|5, 5|4, 1|4 ,10|6 ,13|12 ,13|12, 9|23, 6|7, 3|7, 5|2, 1|2 ,10|6, 6|6, 5|14, 7|14, 6|16, 3|16, 5|14, 6|14, 5|14 ,13|3, 2|3, 7|11, 2|11, 7|6, 7|6, 6|33 ,14|12, 4|12, 3|16 ,18|12, 3|12 ,18|4, 4|4, 3|3, 1|3, 2|6, 9|6, 9|6, 1|6, 2|5, 7|5 ,18|3, 9|3, 9|9 ,18|6, 5|6, 2|2 ,12|2, 9|8 ,3|8 ,9|10 ,9|3, 5|3, 2|3 ,18|3, 7|2, 3|2, 9|]




int: w; % width of the silicon plate
int: n; % number of circuits
array[1..n,1..2] of int: dim; % dimensions of circuits
array[1..n] of var int: area; % area of the circuits
%array[1..n] of var int: diag; % diagonal of the circuits

constraint forall(i in 1..n)(area[i]=dim[i,1]*dim[i,2]);
%constraint forall(i in 1..n)(diag[i]=dim[i,1]*dim[i,1]+dim[i,2]*dim[i,2]);

int: max_l=sum(dim[1..n,2]);
array[1..n,1..2] of var 1..max(w,max_l): pos;

% each circuits inside the silicon plate
constraint forall (i in 1..n) (pos[i,1]<=w-dim[i,1]+1);

% variable to minimize
var int: l=max([pos[i,2] + dim[i,2] |i in 1..n])-1; 

% no overlap between circuits
constraint diffn (pos[1..n,1],pos[1..n,2],dim[1..n,1],dim[1..n,2]) :: domain;

% redundant constraints 
constraint cumulative(pos[1..n,2], dim[1..n,2], dim[1..n,1], w) :: domain;
constraint cumulative(pos[1..n,1], dim[1..n,1], dim[1..n,2], l) :: domain;

% break simmetry constraint: pos[i,1] <= w-pos[i,1]-dim[i,1]+1
var int: i_max = arg_max(area); 
constraint 2*pos[i_max,1] <= w-dim[i_max,1]+2;
constraint 2*pos[i_max,2] <= l-dim[i_max,2]+2;

% faster understanding to have found the optimal solution
var int: empty_space=w*l-sum(area);
constraint empty_space>=0;


%solve and output
ann: search_ann;
search_ann = priority_search(area,  [int_search([pos[i,2],pos[i,1]], input_order, indomain_min)| i in 1..n],largest, complete);





%search_ann = seq_search([int_search(area, largest, indomain_min),search_pr,int_search(pos[1..n,1], first_fail, indomain_min)]);

%pr_search = priority_search(diag,  [int_search([diag[i],pos[i,2]], most_constrained, indomain_min)| i in 1..n],largest, complete);


% case 7 failures = 5667, same with first_fail and dom_w_deg

%search_ann = int_search(pos[1..n,1], smallest, indomain_min);

% search_ann = int_search(pos[1..n,2], smallest, indomain_min);
% case 7 failures = 13297

%search_ann = int_search(pos[1..n, 1], first_fail, indomain_min);
%search_ann = int_search(pos[1..n, 1], dom_w_deg, indomain_random); 
%search_ann = int_search(pos, first_fail, indomain_random);
%search_ann = int_search(pos, first_fail, indomain_min);


solve :: search_ann minimize l;
%solve minimize l;

output["[[\(w), \(l)],\n"]++["[\(dim[i,1]), \(dim[i,2]), \(pos[i,1]), \(pos[i,2])],\n" | i in 1..n-1]++["[\(dim[n,1]), \(dim[n,2]), \(pos[n,1]), \(pos[n,2])]]"]



% empty space approach
%array[1..w,1..max_l] of var 0..n: plate;
%constraint forall (i in 1..w,j in 1..max_l,k in 1..n) ((pos[k,1..2]=[i,j])<->(forall (s in i..(i+dim[k,1]-1), t in j..(j+dim[k,2]-1))(s<=w/\t<=max_l/\plate[s,t]=k)));
%array[1..w,1..max_l] of var int: empty_space;
%constraint forall(i in 1..w, j in 1..max_l)(if (plate[i,j]=0 /\ j<=l) then empty_space[i,j]=1 else empty_space[i,j]=0 endif);
%var int: empty_area=sum(empty_space);
%solve minimize empty_area;

