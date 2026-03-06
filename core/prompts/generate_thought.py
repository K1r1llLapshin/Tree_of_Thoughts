START_PROMPT ='''You are an expert analyst. Your task is to analyze the user's problem and propose {k} distinct, independent directions or initial steps to solve it. 
Each thought must be specific, logical, and represent a single step in the reasoning process.

Problem: {problem}

Output exactly {k} thoughts in the following strict format (no intro or outro):
Thought 1: [Text of the first thought]
Thought 2: [Text of the second thought]
...
Thought {k}: [Text of the k-th thought]
'''

THOUGHT_PROMPT ='''You are an expert analyst. Your task is to continue the reasoning chain to solve the problem.
Given the original problem and the steps already taken, propose {k} possible logical extensions (next steps) for the last thought.

Original Problem: {problem}

Reasoning History:
{history}

Output exactly {k} new options for the next step in this strict format:
Thought 1: [Text of the first option]
Thought 2: [Text of the second option]
...
Thought {k}: [Text of the k-th option]'''


SUMMARY_PROMPT ='''You are an expert in information synthesis. Your task is to provide a final, complete, and clear answer to the user's problem based on the successful reasoning chain.

Original Problem: {problem}

Successful reasoning chain:
{history}

Based on this logic, write a coherent final response. Do not mention the internal "thought process" or "steps above"—simply provide the high-quality final answer to the user's question.'''