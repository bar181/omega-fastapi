
# Omega_Specs.md

This document details the Omega-AGI format and how it is used within the system. It serves as a guide for developers to understand the structure of Omega-AGI prompts, the requirements for those prompts to be considered valid, and how the system validates and leverages them. We also reference the master Omega-AGI documentation as needed for deeper understanding.

## Overview of the Omega-AGI Format
**Omega-AGI (Ω-AGI)** is a specialized, symbolic instruction language for communicating with AI agents. Unlike plain natural language prompts, Omega-AGI provides a highly structured syntax that aims to make the AI's behavior deterministic, unambiguous, and efficient ([Omega-AGI-Symbolic-Language.md · GitHub](https://gist.github.com/bar181/782cfd01f3fd8a635ea718048c1d1c1e#:~:text=language%2C%20which%20can%20be%20ambiguous,method%20for%20conveying%20complex%20instructions)). It is designed to pack complex instructions into a compact format, enabling the AI to interpret and execute multi-step tasks reliably. Key characteristics of Omega-AGI include:
- **Symbolic Representation**: It uses symbols (like `++`, `^`, `@`, etc.) to represent concepts, sections, or pieces of information, rather than verbose descriptions. This improves token efficiency and consistency ([Omega-AGI-Symbolic-Language.md · GitHub](https://gist.github.com/bar181/782cfd01f3fd8a635ea718048c1d1c1e#:~:text=,reliable%20and%20efficient%20processing%2C%20and)).
- **Structured Execution**: Omega-AGI prompts have a defined structure and grammar (based on EBNF grammar rules) that outline the flow of execution for the agent ([Omega-AGI-Symbolic-Language.md · GitHub](https://gist.github.com/bar181/782cfd01f3fd8a635ea718048c1d1c1e#:~:text=%2A%20Structured%20Execution%3A%20Omega,reflection%20as%20a%20core%2C%20first)). This structure covers everything from initialization, to content generation, to reflection and evaluation phases.
- **Deterministic & Machine-Readable**: The format is meant to be machine-readable above all. An Omega-AGI compliant agent should interpret the same prompt in the same way every time, reducing variability in outputs ([Omega-AGI-Symbolic-Language.md · GitHub](https://gist.github.com/bar181/782cfd01f3fd8a635ea718048c1d1c1e#:~:text=,the%20computational%20burden%20of%20interpretation)). The structure minimizes ambiguous natural language elements.
- **Reflection and Self-Optimization**: Omega-AGI includes built-in support for reflection operators (`∇`, `∇²`) and an optimization operator (`Ω`) that allow the prompt itself to instruct the agent to evaluate and improve its output ([Omega-AGI-Symbolic-Language.md · GitHub](https://gist.github.com/bar181/782cfd01f3fd8a635ea718048c1d1c1e#:~:text=,Facilitates%20systemic%20optimization%2C%20adjusting%20execution)). For example, `∇` might trigger the agent to double-check or analyze its current result before finalizing, and `Ω` can indicate an optimization routine to refine the approach.
- **Modularity and Reusability**: Because prompts are structured and symbolic, parts of a prompt can be reused or adapted easily. Also, an agent can potentially modify or augment a prompt programmatically (though in our current system, prompts are authored by users, not AI).

The Omega-AGI format can be thought of as a "program" for the AI to follow. Just as a programming language has a specific syntax and keywords, Omega-AGI has its own syntax and special tokens that an Omega-aware agent or interpreter will recognize.

Our system is built to support Omega-AGI prompts as the primary input. The FastAPI endpoint expects the `omega` field to contain instructions following this format. We rely on the structure to orchestrate calls to the LLM and handle output logically.

## Required Structure of an Omega-AGI Prompt
An Omega-AGI prompt typically consists of several distinct sections in a specific order. According to the Omega-AGI Instruction Guide (v2.0 by Bradley Ross), a one-shot task prompt often includes the following components ([Omega-AGI-Symbolic-Language.md · GitHub](https://gist.github.com/bar181/782cfd01f3fd8a635ea718048c1d1c1e#:~:text=4,AGI%20Prompts)):

1. **Preamble (Standard Overhead)**: This is usually a sequence of Omega operators at the very beginning of the prompt that set the stage for execution. It may include:
   - Reflection and optimization flags: e.g., `∇²` (to enable meta-reflection) and `Ω(∇ history)=>δ(ts='opt')` (which appears to relate to using historical data for optimization) ([Omega-AGI-Symbolic-Language.md · GitHub](https://gist.github.com/bar181/782cfd01f3fd8a635ea718048c1d1c1e#:~:text=This%20document%20provides%20a%20complete,AGI%20prompt%20engineering)) ([Omega-AGI-Symbolic-Language.md · GitHub](https://gist.github.com/bar181/782cfd01f3fd8a635ea718048c1d1c1e#:~:text=1)).
   - Authentication and security directives: e.g., `AUTH[AGI_BA]` might designate the agent's role or permissions (AGI_BA could stand for an AI Business Analyst persona), and `SECURE_COMM(enc=True)` indicates secure communication mode ([Omega-AGI-Symbolic-Language.md · GitHub](https://gist.github.com/bar181/782cfd01f3fd8a635ea718048c1d1c1e#:~:text=1)).
   - These elements are not the "content" of the prompt but rather configuration. They prepare the agent with how to execute the instructions (e.g., enabling reflection capabilities or defining a profile).
   - *Example Preamble*: `∇²;Ω(∇ history)=>δ(ts='opt');AUTH[AGI_BA];SECURE_COMM(enc=True);`  
     This example means: turn on second-level reflection ([Omega-AGI-Symbolic-Language.md · GitHub](https://gist.github.com/bar181/782cfd01f3fd8a635ea718048c1d1c1e#:~:text=,correction%20strategies%20over%20time)), use optimization based on history, authenticate as AGI_BA profile, and ensure communications are encrypted.

2. **Symbol Definitions (`DEFINE_SYMBOLS{...}`)**: A block that defines all symbols used in the prompt along with their meanings or mappings ([Omega-AGI-Symbolic-Language.md · GitHub](https://gist.github.com/bar181/782cfd01f3fd8a635ea718048c1d1c1e#:~:text=2.%20Symbol%20Definitions%20%28)). This is critical for token efficiency and clarity.
   - The syntax is typically `DEFINE_SYMBOLS{ symbol1="Name1" /*Description1*/, symbol2="Name2" /*Description2*/, ... }`.
   - The symbols are often short tokens like `++`, `^`, `@`, etc., mapped to descriptive identifiers or roles. The comments (`/* ... */`) provide human-readable explanations.
   - **Requirement**: If a symbol will be used later (in memory graph or sections), it *must* be defined here. Conversely, symbols defined but not used are harmless but unnecessary.
   - *Example*: `DEFINE_SYMBOLS{++="HDExecSum" /*Executive Summary: High-Depth Analysis*/, ^="IntroMethod" /*Introduction & Methodology*/, @="CompProfiles" /*Competitor Profiles*/ }`  
     This defines `++` as a placeholder for the Executive Summary section, `^` for Intro/Methodology, `@` for Competitor Profiles, etc. ([Omega-AGI-Symbolic-Language.md · GitHub](https://gist.github.com/bar181/782cfd01f3fd8a635ea718048c1d1c1e#:~:text=2.%20Symbol%20Definitions%20%28)).

3. **Memory Graph (`MEM_GRAPH{...}`)**: An optional but powerful section where you outline the relationships between symbols (sections or components) in a directed graph form ([Omega-AGI-Symbolic-Language.md · GitHub](https://gist.github.com/bar181/782cfd01f3fd8a635ea718048c1d1c1e#:~:text=defined.%203.%20Memory%20Graph%20%28)) ([Omega-AGI-Symbolic-Language.md · GitHub](https://gist.github.com/bar181/782cfd01f3fd8a635ea718048c1d1c1e#:~:text=,%E2%A7%89)).
   - Syntax uses arrows, e.g., `A -> [B, C]` meaning A depends on B and C, or contains information from B and C.
   - This guides the logical flow of information: the agent knows which parts to complete first and how information should propagate. It's like declaring that "to complete section A, you will need content from sections B and C".
   - **Requirement**: All symbols used here should be defined in DEFINE_SYMBOLS. The graph should be acyclic (it doesn't make sense to have circular dependencies).
   - *Example*: `MEM_GRAPH{ ++->[^,@,&,&,⧉+]; ^->[@,&]; ... }`  
     This example (from the Coffee Shop analysis prompt) means the Executive Summary (`++`) draws from Introduction (`^`), Competitor Profiles (`@`), Comparative Analysis (`&` appears twice, possibly two different aspects?), and References (`⧉+`). Also `^` (Intro) depends on `@` and `&` ([Omega-AGI-Symbolic-Language.md · GitHub](https://gist.github.com/bar181/782cfd01f3fd8a635ea718048c1d1c1e#:~:text=,that%20depend%20on%20them%2C%20optimizing)). This informs the agent that it should gather or consider competitor profiles and analysis before writing the executive summary, etc.

4. **Conditional Logic (Optional)**: Omega-AGI can include conditional execution statements such as `IF ... THEN ...` blocks ([Omega-AGI-Symbolic-Language.md · GitHub](https://gist.github.com/bar181/782cfd01f3fd8a635ea718048c1d1c1e#:~:text=4)).
   - They check some condition in memory (e.g., a variable or prior result) and decide whether to execute certain actions.
   - In the example, `IF MEM[report_status] != 'completed' THEN → AGI_Rpt GEN_R(local_coffee_shop_analysis);` means: if in memory the report_status is not completed, then generate a report. `GEN_R` might be a command to generate a full report.
   - **Requirement**: Conditions likely refer to memory keys that either have been set previously in the prompt or are default (like the example assumes a memory key `report_status`).
   - The language likely has a specific syntax for conditions (e.g., `IF <cond> THEN <OmegaCommand>;`).
   - This part is optional; many prompts won’t need it, but it's supported for more dynamic behavior.
   - For a developer, unless you plan on using memory states across runs, you might not include conditions in initial prompts.

5. **Formatting and Type Settings**: Commands to set how the output should be formatted or the style/tone of the output ([Omega-AGI-Symbolic-Language.md · GitHub](https://gist.github.com/bar181/782cfd01f3fd8a635ea718048c1d1c1e#:~:text=5,Settings)).
   - Examples from the guide: `→ AGI_Rpt FMT_R(fmt="TXT", d="H");` and `→ AGI_Rpt SET_T(t=MktExpertLevel);`.
   - `FMT_R(fmt="TXT", d="H")` might mean "format the report as plain text with headings" (d="H" could indicate including headings).
   - `SET_T(t=MktExpertLevel)` could set the tone/rigor to "Marketing Expert Level".
   - These instructions tell the agent about the desired output format (e.g., maybe you could set `fmt="HTML"` for HTML output, or `d="L"` for including links, guessing from context).
   - **Requirement**: These should appear before content generation. They configure the `AGI_Rpt` (the agent's report generator module, presumably) with how to produce output.
   - They are optional if you are okay with defaults (likely default is plain text, moderate detail).
   - As an Omega prompt author, you might use these to ensure the style is correct. For instance, if you want a JSON output, there might be a format setting for JSON (if supported by Omega).

6. **Neural Block (Optional)**: `NEURAL_BLOCK("...")` allows you to insert a block of instructions or content that should be handled by a neural network as a black box ([Omega-AGI-Symbolic-Language.md · GitHub](https://gist.github.com/bar181/782cfd01f3fd8a635ea718048c1d1c1e#:~:text=6)) ([Omega-AGI-Symbolic-Language.md · GitHub](https://gist.github.com/bar181/782cfd01f3fd8a635ea718048c1d1c1e#:~:text=,sensitivity%20and%20criticality%20of%20each)).
   - This is essentially an escape hatch: if there is something that doesn't fit the formal Omega-AGI language, you can wrap it in NEURAL_BLOCK and the agent/LLM will treat the inner content as raw instruction or data.
   - In the example prompt, `NEURAL_BLOCK("CoffeeShop_Competitor_Analysis");` is likely a call to a specific trained network or just a marker for context. It might load a specialized context or trigger a particular capability for coffee shop competitor analysis.
   - For our implementation, we may not have special neural modules. But if a prompt uses NEURAL_BLOCK, our agent will likely just include that text to the LLM as is. It’s optional and can be omitted if not needed.
   - **Requirement**: Use NEURAL_BLOCK only when necessary (for unstructured data or external context). Otherwise, keep everything in Omega structure.

7. **Section Definitions (`WR_SECT` loops)**: This is the core content generation part of the prompt ([Omega-AGI-Symbolic-Language.md · GitHub](https://gist.github.com/bar181/782cfd01f3fd8a635ea718048c1d1c1e#:~:text=7.%20Section%20Definitions%20%28)).
   - `WR_SECT` stands for "Write Section". Each `WR_SECT(symbol, t=symbol, d="...")` call directs the agent to write a section corresponding to a symbol, with a title and description.
   - Format: `→ AGI_Rpt WR_SECT(X, t=X, d="Instructions for this section");`
     - The arrow `→ AGI_Rpt` means we are invoking the report-writing agent to execute a command.
     - `t=X` likely sets the title using symbol X's defined name (or uses X itself as a key).
     - `d="..."` is the actual content directive for that section, written in a mix of symbolic and brief natural language.
   - Several `WR_SECT` commands are typically listed in order, each for one symbol/section. They effectively break the output into manageable pieces.
   - Inside the `d="..."` description, the prompt author will often use the symbols and sometimes quoted words (likely treated as is) to instruct what to include.
   - In the example:
     ``` 
     → AGI_Rpt WR_SECT(++, t=++, d="Exec summary (3+ parag). \"Synth\" \"LocalShop\" \"CompMarkAnalysis\". Highlight key competitor strategies, comparative insights, and core \"MarketRecs\". Concise, \"AI\".");
     ```
     This is instructing the AGI to write the Executive Summary section (symbol `++`), title it with whatever `++` stands for, and in the description: 
     - It says Exec summary 3+ paragraphs, includes certain keywords in quotes (Synth, LocalShop, CompMarkAnalysis, MarketRecs) which are likely defined symbols or shorthand for concepts, and style hints like "Concise, AI" (maybe meaning concise and in an AI-professional tone).
   - **Requirement**: Each WR_SECT should refer to a symbol defined in DEFINE_SYMBOLS. The sequence of WR_SECT defines the structure of the final output. A prompt should have at least one WR_SECT (otherwise no content is being explicitly generated).
   - The agent will follow these instructions to generate each part. If any section is very complex, the LLM might do an internal breakdown, but as far as prompt format, this is how you specify content.

8. **Evaluation Loop (`FOR...DO...EVAL_SECT`)**: Optional, for quality control ([Omega-AGI-Symbolic-Language.md · GitHub](https://gist.github.com/bar181/782cfd01f3fd8a635ea718048c1d1c1e#:~:text=8.%20Evaluation%20Loop%20%28)).
   - Syntax: `FOR sec IN {list of symbols} DO → AGI_Rpt EVAL_SECT(sec, th=90, iter=3);`
   - This instructs the agent to iterate through each section and evaluate its quality, with a threshold and iteration count.
   - In the example, `th=90` could represent a quality score threshold (maybe out of 100) and `iter=3` means allow up to 3 attempts to improve if below threshold.
   - `EVAL_SECT(sec, ...)` likely triggers the agent to review that section’s content (possibly by feeding it back into the LLM with some prompt like "critique this section") and then either directly improve it or provide feedback so that a subsequent generation can improve it.
   - **Requirement**: If used, sec (the section symbol or list of symbols) should be those that were generated. Typically, you'd evaluate all major sections. It's optional; if high quality isn't critical or time is short, you might skip this to save tokens.
   - Our implementation might not fully automate re-writing sections, but conceptually, if we detect issues, we could re-run with adjustments. The Omega format has this built in to allow self-improvement.

9. **Finalization**: The Omega format doesn't explicitly have an "end" marker; the script itself is the set of instructions. Once the agent has executed all commands (wrote all sections, did evaluations), the output is considered complete. The final answer returned to the user is essentially the concatenation of all the written sections (assuming a report context). If it were a simpler query, it might just be one section or even a direct answer without formal sections.

In summary, an **Omega-AGI prompt** is structured very much like a small program: it sets up some variables (symbols), optionally sets a plan (memory graph), then runs through generating content, and possibly evaluates it. All these parts use a special syntax that the agent (and LLM) need to understand.

Our system does not yet implement a parser to enforce every rule of this structure, but it expects prompts roughly in this shape. When writing Omega prompts, ensure you include at least the essentials: symbol definitions and one or more `WR_SECT` instructions. The richer features (memory graphs, eval loops) can be added as needed.

## Validation Requirements for Omega Prompts
For an Omega-AGI prompt to be processed correctly, it should meet certain criteria. These requirements are based on the design of Omega-AGI and practical considerations for our implementation:

- **Presence of Key Sections**: At minimum, the prompt should define any symbols it uses and include at least one content generation command (`WR_SECT` or a `GEN` command) that produces output. A prompt that has only a preamble and symbols but no section to output will result in no answer.
- **Define-Before-Use**: Any symbol used in `WR_SECT`, `MEM_GRAPH`, or other commands must be defined in the `DEFINE_SYMBOLS` block ([Omega-AGI-Symbolic-Language.md · GitHub](https://gist.github.com/bar181/782cfd01f3fd8a635ea718048c1d1c1e#:~:text=,%E2%A7%89)). Our system may check the text to ensure that, for example, if it sees `WR_SECT(X, ...)`, then `X` (or whatever symbol is inside) was introduced in a prior `DEFINE_SYMBOLS`. If not, that's an error.
- **Balanced Syntax**: All brackets and parentheses must be properly closed:
  - Every `{` must have a matching `}` (for DEFINE_SYMBOLS, MEM_GRAPH).
  - Every `(` has a `)` (for function-like syntax such as `Ω(...)` or `WR_SECT(...)`).
  - Comments `/* ... */` should be properly closed.
  - If any are mismatched, the agent might not parse it right, and our validator will likely flag it. For example, a missing brace in DEFINE_SYMBOLS could confuse everything after it.
- **Known Commands**: Use only Omega-AGI defined operators and commands. These include:
  - The reflection and optimization operators: `∇`, `∇²`, `Ω`.
  - The `DEFINE_SYMBOLS`, `MEM_GRAPH`, `WR_SECT`, `EVAL_SECT`, and perhaps `GEN_R`, `FMT_R`, `SET_T`, `NEURAL_BLOCK`, `AUTH`, `SECURE_COMM`, etc., as seen in the guide. Using an arbitrary or unknown token (e.g., if you guess a command that isn't defined) could lead to undefined behavior. Our system might not explicitly catch unknown commands, but the LLM could be confused by them.
  - If unsure, stick to the patterns seen in examples or documented features. As Omega-AGI evolves, new commands might be introduced, but then the agent must be updated to handle them.
- **Logical Consistency**: The prompt should make logical sense:
  - The memory graph should not have contradictions (like `A->B` and also `B->A` forming a cycle).
  - Symbols should be used in a consistent way (for instance, if `&` is used for two different things in comments, that's confusing; each symbol should have one purpose).
  - If the prompt is asking for something the model can’t do (e.g., an overly long report with limited context length), the output might be truncated. So there is a practical limit to how much you can ask for in one go.
- **No Overlapping Sections**: Avoid generating the same content twice. For example, do not have two `WR_SECT` for the same symbol unless intentional (the second would overwrite or append? It's unclear, better to avoid).
- **Use of Reflection/Eval**: If you include `EVAL_SECT`, ensure you also provided criteria (threshold and iter count). If you just put `EVAL_SECT(sec)` without parameters, it might default to something or cause an error. Similarly, using `Ω(∇ history)=>δ(ts='opt')` in preamble suggests there's some historical optimization; our initial agent might not actually use history (since we aren't persisting it), but including it doesn't break anything, it just won't have any past data to use. It's fine to include for future compatibility.
- **Encoding of Special Characters**: Omega uses some Unicode characters like `∇` (nabla) and `Ω` (Omega symbol). These should be included as such. If you are writing an Omega prompt in a normal text editor or JSON, ensure it is encoded in UTF-8. Our API expects UTF-8 JSON, so it should handle these characters. Just be cautious if copying from some sources that they don't get lost. Alternatively, one could use ASCII placeholders if defined (the master doc might allow some fallback, but it's not mentioned explicitly). We recommend using the actual symbols.
- **Master Document Reference**: For full details, one should refer to the **Omega-AGI Instruction Guide v2.0** by Bradley Ross, which is the authoritative source on the syntax and usage ([Omega-AGI-Symbolic-Language.md · GitHub](https://gist.github.com/bar181/782cfd01f3fd8a635ea718048c1d1c1e#:~:text=This%20document%20provides%20a%20complete,AGI%20prompt%20engineering)). That guide includes examples and deeper explanations of each component of the language, as well as the rationale behind them. Our system aims to align with that spec, and any deviations or limitations are due to implementation simplicity at this stage.

In practice, when you send an Omega prompt to the system:
- If it's well-formed, the agent will either run it in one shot (giving the whole prompt to the LLM) or step by step. The better structured it is, the more likely the LLM will follow it exactly and produce the desired structured output.
- If it's ill-formed, a few things could happen: The agent might catch a problem and return an error. Or the agent might pass it through and the LLM might get confused and produce an incorrect or incomplete result. Therefore, following the required structure is important for getting good results.

Our **validation** (as described in Data_Specs) will catch some errors, but not everything. It remains the developer's responsibility to craft the Omega prompt carefully. Over time, we plan to improve the validator or even have the agent attempt to correct minor prompt issues (given Omega's self-improvement ethos).

## Reference to Master Omega-AGI Document
For a comprehensive understanding of Omega-AGI syntax and principles, refer to the master document: *"Omega-AGI Instruction Guide: A Comprehensive Overview (v2.0)" by Bradley Ross*. This guide outlines the methodology, structural components, and step-by-step instructions for effective Omega-AGI prompt engineering ([Omega-AGI-Symbolic-Language.md · GitHub](https://gist.github.com/bar181/782cfd01f3fd8a635ea718048c1d1c1e#:~:text=This%20document%20provides%20a%20complete,AGI%20prompt%20engineering)). It covers in detail:
- The philosophy and goals of Omega-AGI (determinism, efficiency, etc.) ([Omega-AGI-Symbolic-Language.md · GitHub](https://gist.github.com/bar181/782cfd01f3fd8a635ea718048c1d1c1e#:~:text=,the%20computational%20burden%20of%20interpretation)).
- The full breakdown of the language’s syntax (including any grammar definitions in EBNF).
- Examples of one-shot prompts and how they are constructed from start to finish.
- Explanation of reflection operators and when to use them ([Omega-AGI-Symbolic-Language.md · GitHub](https://gist.github.com/bar181/782cfd01f3fd8a635ea718048c1d1c1e#:~:text=,Facilitates%20systemic%20optimization%2C%20adjusting%20execution)).
- Best practices and common patterns for designing prompts (like how to choose symbols, how to structure memory graphs for various tasks, etc.).
- Limitations and planned extensions of the language (as of v2.0).

We highly encourage reading that document if you intend to author complex Omega-AGI prompts. It will serve as the primary reference for anything not explicitly covered in our documentation. Our Omega-AGI support is built to align with that spec, and any updates in the Omega-AGI standard may require updating the system accordingly.

In conclusion, Omega-AGI format is the backbone of this AI system's communication. By adhering to its structure and guidelines, developers can harness advanced AI behaviors (like multi-step reasoning and self-evaluation) in a controlled and consistent manner. This documentation plus the Omega-AGI guide should together provide a self-contained resource to construct and utilize Omega-AGI prompts effectively in the system.

---
