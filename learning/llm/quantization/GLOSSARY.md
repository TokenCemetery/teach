---
title: Glossary
description: "Canonical terms for LLM quantization"
type: glossary
---

# Quantization Glossary

Canonical terms for number formats, quantization methods, the hardware they run on, and how their cost is measured. In this workspace "quantization" always means reducing the precision of a trained model's numbers; it never means discretising inputs.

## Terms

**Absmax quantization**:
Symmetric quantization whose clipping range is the largest absolute value among the values sharing a scale, so nothing is clipped and the scale is that value divided by the largest integer level.
_Avoid_: max scaling, naive quantization

**Act-order**:
A GPTQ option that quantizes a layer's columns in order of decreasing activation size, by sorting them on the diagonal of the Hessian. It is documented in the authors' code, not in the paper.
_Avoid_: desc_act without introducing it, reorder trick (the AWQ paper's name for a GPTQ variant)

**Activation**:
A tensor computed during the forward pass, such as the input to a linear layer, as opposed to a stored weight. Its values depend on the input, so its range is only known at run time or estimated from a calibration set.
_Avoid_: hidden state (fine for the residual stream specifically), feature map

**Affine quantization**:
Quantization with both a scale and a zero point, so the integer grid can sit asymmetrically around zero and cover a range such as [-0.2, 1.5] without wasting levels.
_Avoid_: asymmetric quantization (accepted alias, but use one term), uniform quantization (also true of symmetric)

**Arithmetic intensity**:
The number of arithmetic operations a computation performs per byte it moves from memory, which decides whether it is memory-bound or compute-bound on a given chip.
_Avoid_: operational intensity, FLOP-to-byte ratio (accepted in a formula)

**Bit width**:
The number of bits used to store one quantized value, not counting the bits spent on its scale and zero point. See effective bits per weight for the total.
_Avoid_: precision (ambiguous with mantissa bits), bit depth

**Block-scaled format**:
A format in which a small block of values, such as 32, shares one scale stored alongside them, so the element type can be very narrow. MXFP4 and NVFP4 are examples, as are GGUF's block types.
_Avoid_: microscaling (that is one family, OCP's MX), grouped format

**Calibration set**:
A small sample of representative inputs run through the model to collect activation statistics, which a post-training method uses to choose ranges or to weigh rounding errors. It is not training data and is never backpropagated through by PTQ.
_Avoid_: training set, calibration dataset (fine, but not "calibration data" for the statistics themselves)

**Clipping error**:
The error from values outside the clipping range being clamped to its ends.
_Avoid_: saturation error, overflow

**Clipping range**:
The interval of real values a quantizer maps onto its integer grid; values outside it are clamped to the nearest end. Choosing it trades clipping error against rounding error.
_Avoid_: dynamic range (that is a property of the format), quantization range

**Compute-bound**:
A workload whose speed is limited by arithmetic throughput rather than by moving bytes, typical of prefill and of large-batch decode. Quantizing only the weights does not speed it up, and can slow it down.
_Avoid_: FLOP-bound (fine, but use one term)

**Dequantization**:
Mapping a quantized integer back to an approximate real value with its scale and zero point, either to compute in higher precision or to inspect the error.
_Avoid_: unquantization, decompression

**Dynamic quantization**:
Computing an activation's scale at run time from the values actually present, rather than fixing it ahead of time from a calibration set. Contrast static quantization.
_Avoid_: on-the-fly quantization, runtime quantization

**Effective bits per weight**:
The average storage per weight once scales, zero points and any other per-group metadata are included, for example about 4.5 for 4-bit weights with a 16-bit scale per group of 32.
_Avoid_: bpw without defining it, bit width (which excludes the metadata)

**Exponent bits**:
The bits of a floating-point format that set the power of two a value is scaled by, and so its dynamic range.
_Avoid_: range bits

**Fake quantization**:
Quantizing and immediately dequantizing a tensor in the forward pass, so training sees the rounding and clamping error while the arithmetic stays in floating point.
_Avoid_: simulated quantization (accepted alias, but use one term), quantization noise injection

**Flip**:
An answer that changes from correct to incorrect, or from incorrect to correct, between a baseline model and its quantized version on the same question. Flips in both directions cancel in an accuracy average, so they are counted separately.
_Avoid_: answer change (also counts incorrect to incorrect), regression (one direction only)

**GGUF**:
llama.cpp's single-file model format, which stores tensors, often in its own block quantization types, together with the tokenizer and model metadata.
_Avoid_: GGML (the library and an older format), llama format

**GPTQ**:
A post-training weight quantization method that quantizes a layer's weights one column at a time and updates the not-yet-quantized weights to compensate for each rounding error, using second-order information from calibration activations.
_Avoid_: GPT quantization, generic for any 4-bit checkpoint

**Granularity**:
How many values share one scale and zero point: a whole tensor (per-tensor), one output channel (per-channel), one token (per-token), or a fixed-size group within a channel (per-group).
_Avoid_: resolution, quantization level

**Group size**:
The number of consecutive values that share one scale in per-group quantization, such as 32 or 128.
_Avoid_: block size (accepted where a format calls it that, such as MX or GGUF)

**Hessian**:
In GPTQ, the matrix `H = 2 X X^T` built from a layer's calibration inputs, with one row and column per input feature. It records which features move together and is shared by every row of the layer's weights.
_Avoid_: curvature matrix, covariance matrix (close, but not the same object)

**Importance matrix**:
In llama.cpp, per-weight importance estimated from activations on a calibration text, used to weight the rounding error when choosing each block's scale.
_Avoid_: imatrix in prose without introducing it

**Kernel**:
The GPU routine that performs one operation, such as a matrix multiplication in a given quantization scheme. A scheme runs fast only where a kernel for it exists on the hardware.
_Avoid_: operator (broader), implementation

**KL divergence**:
How far the quantized model's next-token distribution is from the baseline's, averaged over a dataset's tokens. It is 0 when the two agree exactly and needs no labelled answers.
_Avoid_: KLD without defining it, distance (ambiguous)

**KV-cache quantization**:
Storing the cached attention keys and values in fewer bits, to cut the memory that grows with context length and batch size.
_Avoid_: cache compression (also covers eviction), KV quantization of weights

**Loss scaling**:
Multiplying the loss by a constant before backpropagation so small gradients stay representable in a narrow-range format such as fp16, then dividing the constant out before the weight update.
_Avoid_: gradient scaling (ambiguous with gradient clipping)

**Machine epsilon**:
The gap between 1 and the next representable value above it in a floating-point format, equal to 2 to the power of minus the number of mantissa bits.
_Avoid_: unit roundoff (half of this under round-to-nearest), precision

**Mantissa bits**:
The bits of a floating-point format that set how finely values are spaced within one power of two, and so its precision.
_Avoid_: significand (correct but use one term), fraction bits

**Massive activation**:
A single activation value in an LLM that is orders of magnitude larger than the rest, appearing at a fixed dimension and at specific tokens such as the first one.
_Avoid_: outlier feature (a related but different pattern), spike

**Memory-bound**:
A workload whose speed is limited by how fast bytes move from memory rather than by arithmetic, typical of small-batch decode, where every weight is read once per generated token.
_Avoid_: bandwidth-bound (fine, but use one term), IO-bound

**Mixed-precision decomposition**:
Splitting a matrix multiplication so the few outlier feature dimensions are computed in 16-bit and the rest in int8, the core of LLM.int8().
_Avoid_: outlier splitting, mixed precision (broader)

**Native format**:
A number format a chip's matrix units multiply in directly, as opposed to a storage-only format that must be converted to a native one before the multiplication.
_Avoid_: supported format (ambiguous between storage and compute)

**Noise floor**:
The run-to-run and sampling variation of a score, below which a difference between a baseline and a quantized model cannot be told from chance.
_Avoid_: margin of error (the interval is how the floor is reported), tolerance

**Outlier feature**:
A hidden-state dimension in which a transformer's activations are consistently much larger than in the others, across most tokens and layers.
_Avoid_: outlier channel (accepted for the matching weight channel), emergent feature without the word outlier

**Perplexity**:
The exponential of the average negative log-likelihood a model assigns to a text, used as a quick proxy for how much a change hurt the model.
_Avoid_: PPL in prose without introducing it, accuracy

**Post-training quantization**:
Quantizing an already-trained model without further training, using at most a small calibration set.
_Avoid_: PTQ in prose without introducing it, one-shot quantization

**Quantization**:
Representing a model's real-valued numbers on a smaller set of levels with fewer bits, at the cost of a bounded approximation error.
_Avoid_: compression (broader), discretisation

**Quantization config**:
The `quantization_config` entry in a model's `config.json`, whose `quant_method` and other keys tell a loader which method, bit width and group size the stored tensors use.
_Avoid_: quantize config (a separate file some tools write), metadata

**Quantization-aware training**:
Training or fine-tuning a model with fake quantization in the forward pass, so the weights adapt to the rounding they will face.
_Avoid_: QAT in prose without introducing it, quantized training (that computes in low precision)

**Ridge point**:
The arithmetic intensity at which a chip's peak arithmetic rate and its memory bandwidth take the same time, below which a computation is memory-bound and above which it is compute-bound.
_Avoid_: roofline knee, crossover

**Rotation**:
Multiplying a layer's activations and weights by an orthogonal matrix and its transpose, which leaves the layer's output unchanged but spreads outliers across many channels so they quantize better.
_Avoid_: Hadamard transform (one choice of rotation), incoherence processing (the general idea)

**Round-to-nearest**:
Quantizing each value independently to its nearest grid level, with no data and no error compensation. The baseline every other post-training method is compared against.
_Avoid_: RTN in prose without introducing it, naive quantization

**Rounding error**:
The error from a value inside the clipping range being moved to the nearest grid level; at most half a step for round-to-nearest.
_Avoid_: quantization noise (accepted for the combined error), precision loss

**Safetensors**:
A tensor file format with an 8-byte header length, a JSON header of tensor names, dtypes, shapes and offsets, and then raw data. It stores tensors only, so the quantization scheme is described in the quantization config.
_Avoid_: checkpoint (the whole set of files), weights file

**Salient channel**:
An input channel of a weight matrix whose quantization error matters most, found in AWQ by the size of the activation it meets rather than by the size of its own weights.
_Avoid_: important weight (fine in prose), outlier channel (the weight-side name for an outlier feature)

**Scale**:
The real-valued step size between adjacent integer levels of a quantizer, so that a real value is approximately the scale times its integer.
_Avoid_: step (fine in a formula), multiplier

**Static quantization**:
Fixing an activation's scale ahead of time from a calibration set, so no statistics are computed at run time. Contrast dynamic quantization.
_Avoid_: offline quantization

**Straight-through estimator**:
Treating the rounding step as the identity function in the backward pass, so a gradient can flow through an operation whose true derivative is zero almost everywhere.
_Avoid_: STE in prose without introducing it, surrogate gradient (broader)

**Super-block**:
In a GGUF k-quant, a group of 256 weights split into sub-blocks that each have their own scale, with those scales quantized against a 16-bit super-block scale.
_Avoid_: block (the 32-weight unit of the legacy types)

**Symmetric quantization**:
Quantization with the zero point fixed at zero, so the grid is centred on zero and only a scale is stored.
_Avoid_: scale-only quantization

**Weight-only quantization**:
Storing weights in low precision and dequantizing them inside the kernel, while activations and the arithmetic stay in 16-bit. Written WxA16, such as W4A16.
_Avoid_: mixed-precision quantization (broader)

**WxAy notation**:
Shorthand for a scheme's weight and activation bit widths, such as W8A8 for 8-bit weights and activations, sometimes with KVz for the KV cache.
_Avoid_: writing int4 when the activations are not also int4

**Zero point**:
The integer that represents real zero in affine quantization, chosen so zero is exactly representable.
_Avoid_: offset, bias
