---
title: "शब्दावली"
description: "LLM pretraining के मानक शब्द"
type: glossary
---

# LLM Pretraining शब्दावली

random initialization से बड़े पैमाने पर model train करने के मानक शब्द: data और compute budget किन चीज़ों से बनते हैं, और memory तथा computation को कई devices में कैसे बाँटा जाता है।

## शब्द

**Activation checkpointing**:
Forward pass के दौरान बीच के activations को हटा देना और backward pass में उन्हें दोबारा compute करना, यानी कम memory के बदले ज़्यादा compute देना।
_बचें_: gradient checkpointing (व्यवहार में यह ज़्यादा चलने वाला नाम है, पर checkpoint activations होते हैं, gradients नहीं, और यह अस्पष्ट नाम इस बारे में भ्रम पैदा करता है कि किसका सौदा हो रहा है)

**Compute-optimal**:
Parameter count और training tokens के बीच के सौदे का वह बिंदु जो तय training compute budget पर loss को सबसे कम करता है, उस बड़े model के मुक़ाबले जो इस बिंदु के हिसाब से कम tokens पर train हुआ हो।
_बचें_: optimal (अस्पष्ट है कि किस चीज़ के लिए optimal; हमेशा "compute" या "inference" के साथ जोड़ें, ताकि साफ़ हो कि कौन-सा budget तय है)

**Data parallelism**:
Training batch को ऐसे devices में बाँटना जिनमें से हर एक के पास model की पूरी copy होती है, हर device अलग से gradients निकालता है, और optimizer step से पहले उन्हें all-reduce से synchronize किया जाता है।
_बचें_: distributed training (data parallelism उसका एक रूप है; यह सामान्य शब्द छिपा देता है कि कौन-सा resource बँट रहा है)

**Deduplication**:
Tokenization से पहले training corpus से लगभग-एक-जैसे या हू-ब-हू एक-जैसे documents हटाना, क्योंकि दोहराया गया text memorization और बर्बाद compute की एक प्रमुख वजह है।
_बचें_: dedup (अनौपचारिक रूप से ठीक है, पर concept तय हो जाने के बाद शब्दावली इसे पूरा लिखती है)

**Gradient clipping**:
Optimizer step के gradient इस्तेमाल करने से पहले उसे अनुपात में rescale करना, ताकि उसका global norm चुनी हुई सीमा से कभी ऊपर न जाए। इससे एक अकेला update कितना बड़ा हो सकता है उस पर रोक लगती है, चाहे असामान्य रूप से बड़ा gradient किसी भी वजह से बना हो।
_बचें_: gradient clamping (clamping का मतलब आम तौर पर हर value को अलग से सीमित करना होता है; यहाँ clipping पूरे gradient vector को एक ही factor से rescale करके उसका norm सीमित करती है)

**Learning rate warmup**:
Training के पहले हिस्से में learning rate को शून्य के आसपास से उसके इच्छित अधिकतम तक धीरे-धीरे बढ़ाना, बजाय इसके कि शुरू से ही अधिकतम पर चलें, ताकि network के सबसे कम जानकारी वाले शुरुआती updates का weights पर असर छोटा रहे।
_बचें_: burn-in (दूसरे क्षेत्रों का शब्द जो स्थिर होने की अवधि के लिए आता है; यह workspace warmup का इस्तेमाल ख़ास तौर पर learning-rate की इस बढ़त के लिए करता है)

**Loss spike**:
Run के बीच में training loss का अचानक और तेज़ उछाल, जो आम तौर पर numerically अस्थिर batch या जमा हुए optimizer-state drift से आता है, और जिसे साधारण noise से इस आधार पर अलग किया जाता है कि loss अपने-आप लौटता है या नहीं।
_बचें_: divergence (loss spike के न लौटने पर जो नतीजा निकलता है वह divergence है; दोनों एक ही घटना नहीं हैं)

**Pipeline parallelism**:
Model की layers को devices में बाँटना, जहाँ हर device के पास stack का एक लगातार हिस्सा होता है और वह activations अगले device को देता है, और हर device को व्यस्त रखने के लिए कई micro-batches उसमें pipeline की तरह बहाए जाते हैं।
_बचें_: model parallelism (यह व्यापक शब्द है जिसके अंतर्गत यह और tensor parallelism दोनों आते हैं; फ़र्क़ मायने रखने लगे तो ख़ास वाला शब्द इस्तेमाल करें)

**Scaling law**:
Model के loss और उसे train करने में लगे compute, parameter count या data के बीच का अनुभव-आधारित power-law संबंध, जिसका इस्तेमाल training run का loss उसकी क़ीमत चुकाने से पहले अनुमान लगाने में होता है।
_बचें_: scaling curve (scaling law वह fit किया हुआ संबंध है; curve उसका एक plot है)

**Tensor parallelism**:
किसी एक layer की weight matrices को devices में बाँटना, ताकि एक matrix multiplication हर device के आंशिक गुणनफलों के योग के रूप में compute हो, और इसकी क़ीमत हर बँटी हुई layer पर एक communication step है।
_बचें_: model parallelism (यह व्यापक शब्द है जिसके अंतर्गत यह और pipeline parallelism दोनों आते हैं)

**Tokens-per-parameter ratio**:
Training tokens की संख्या को model के parameter count से भाग देने पर मिलने वाली संख्या, वह अकेली संख्या जिसके चारों ओर compute-optimal training plan बनता है।
_बचें_: data-to-model ratio (साहित्य में यह उलटी राशि के लिए बेमेल ढंग से इस्तेमाल होता है; यह workspace हमेशा tokens को parameters से भाग देने की बात करता है)

**ZeRO stage**:
Data-parallel devices में बाँटी जाने वाली state के तीन बढ़ते स्तरों में से एक: optimizer state (stage 1), optimizer state और gradients (stage 2), या optimizer state, gradients और parameters (stage 3), और हर स्तर कम per-device memory के बदले ज़्यादा communication देता है।
_बचें_: FSDP (FSDP, PyTorch का ZeRO stage 3 जैसी sharding का implementation है; ZeRO बुनियादी तकनीक है, और यह workspace विचार की बात करते समय तकनीक का नाम और API की बात करते समय FSDP इस्तेमाल करता है)
