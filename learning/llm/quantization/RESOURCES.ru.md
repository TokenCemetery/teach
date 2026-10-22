---
title: "Ресурсы"
description: "Проверенные источники по квантизации LLM"
type: resources
---

# Ресурсы по квантизации

## Знания

### Основы

- [Научная статья: "A White Paper on Neural Network Quantization", Nagel et al., 2021](https://arxiv.org/abs/2106.08295)
  Введение объёмом с учебник от Qualcomm AI Research: аппаратная мотивация, равномерный аффинный квантизатор, выбор диапазона, гранулярность, конвейеры PTQ и QAT и порядок отладки. Использовать для: отображения и выбора диапазона на этапах 2 и 6, из первоисточника, а не из пересказа.
- [Научная статья: "A Survey of Quantization Methods for Efficient Neural Network Inference", Gholami et al., 2021](https://arxiv.org/abs/2103.13630)
  Широкий обзор равномерных и неравномерных квантизаторов, гранулярности, PTQ против QAT и смешанной точности. Использовать для: того, чтобы поместить метод в более широкое семейство до чтения его собственной статьи.
- [Научная статья: "Quantization and Training of Neural Networks for Efficient Integer-Arithmetic-Only Inference", Jacob et al., 2017](https://arxiv.org/abs/1712.05877)
  Схема инференса только на целочисленной арифметике, лежащая в основе большинства развёртываний int8: аффинное отображение с точно представимым нулём и обучение с имитацией квантизации. Использовать для: происхождения соглашения о масштабе и нулевой точке.

### Числовые форматы

- [Научная статья: "Mixed Precision Training", Micikevicius et al., 2017](https://arxiv.org/abs/1710.03740)
  Обучение в fp16 с главной копией в fp32 и масштабированием потерь и то, почему узкий диапазон fp16 делает это масштабирование необходимым. Использовать для: того, чего стоят пять бит экспоненты у fp16.
- [Научная статья: "A Study of BFLOAT16 for Deep Learning Training", Kalamkar et al., 2019](https://arxiv.org/abs/1905.12322)
  Доводы в пользу bf16, который сохраняет экспоненту fp32 и отбрасывает биты мантиссы. Использовать для: того, почему для обучения диапазон оказался важнее точности.
- [Научная статья: "FP8 Formats for Deep Learning", Micikevicius et al., 2022](https://arxiv.org/abs/2209.05433)
  Восьмибитные кодировки с плавающей точкой E4M3 и E5M2, их специальные значения и результаты обучения и инференса в них. Использовать для: того, для чего нужен каждый вариант fp8.
- [Научная статья: "Microscaling Data Formats for Deep Learning", Rouhani et al., 2023](https://arxiv.org/abs/2310.10537)
  Блочно-масштабируемые форматы, в которых блок узких элементов делит один масштаб в виде степени двойки; основа форматов OCP MX. Использовать для: того, как MXFP4 и родственные форматы хранят блок.
- [Статья: "Introducing NVFP4 for Efficient and Accurate Low-Precision Inference", NVIDIA Technical Blog](https://developer.nvidia.com/blog/introducing-nvfp4-for-efficient-and-accurate-low-precision-inference/)
  4-битный формат с плавающей точкой одного производителя, с меньшим блоком и более тонким масштабом, чем у MXFP4. Использовать для: того, чем NVFP4 отличается от MXFP4, читая как документацию производителя.

### Выбросы

- [Научная статья: "LLM.int8(): 8-bit Matrix Multiplication for Transformers at Scale", Dettmers et al., 2022](https://arxiv.org/abs/2208.07339)
  Открывает измерения признаков-выбросов, которые ломают int8 в больших трансформерах, и оставляет их в 16 битах с помощью декомпозиции со смешанной точностью. Использовать для: того, где появляются выбросы, и первого способа с ними справиться.
- [Научная статья: "Massive Activations in Large Language Models", Sun et al., 2024](https://arxiv.org/abs/2402.17762)
  Отдельные активации на порядки больше остальных, в фиксированных измерениях и на определённых токенах, действующие как выученные смещения. Использовать для: второго паттерна выбросов и того, почему это не шум.
- [Научная статья: "Quantizable Transformers: Removing Outliers by Helping Attention Heads Do Nothing", Bondarenko et al., 2023](https://arxiv.org/abs/2306.12929)
  Связывает выбросы с тем, что головы внимания учатся ничего не делать, и убирает их изменением архитектуры во время обучения. Использовать для: того, зачем выбросы вообще существуют.

### Посттренировочная квантизация

- [Научная статья: "The case for 4-bit precision: k-bit Inference Scaling Laws", Dettmers and Zettlemoyer, 2022](https://arxiv.org/abs/2212.09720)
  Более 35 000 zero-shot-экспериментов по разрядностям, типам данных и размерам блока, по которым 4 бита почти всегда оптимальны при фиксированном числе бит модели, а помогают лишь малые блоки и выбор типа данных. Использовать для: того, почему 4-битные веса стали вариантом по умолчанию и что даёт размер блока.
- [Научная статья: "Up or Down? Adaptive Rounding for Post-Training Quantization", Nagel et al., 2020](https://arxiv.org/abs/2004.10568)
  Показывает, что округление каждого веса к ближайшему уровню не оптимально для выхода слоя, и вместо этого обучает направление округления. Использовать для: того, почему округление к ближайшему оставляет точность на столе.
- [Научная статья: "Optimal Brain Compression", Frantar and Alistarh, 2022](https://arxiv.org/abs/2208.11580)
  Точный послойный метод квантизации, который GPTQ делает быстрым, с обновлением, тратящим ошибку одного веса на остальные. Использовать для: родословной GPTQ.
- [Научная статья: "GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers", Frantar et al., 2022](https://arxiv.org/abs/2210.17323)
  Одношаговая 3- и 4-битная квантизация весов с приближённой информацией второго порядка в масштабе моделей на 175 млрд параметров. Использовать для: того, как работает GPTQ и что такое его калибровочный набор.
- [Научная статья: "AWQ: Activation-aware Weight Quantization for LLM Compression and Acceleration", Lin et al., 2023](https://arxiv.org/abs/2306.00978)
  Обнаруживает, что небольшая доля каналов весов важнее всего, определяет их по величине активаций и защищает масштабированием по каналам, а не смешанной точностью. Использовать для: того, как работает AWQ и почему ему не нужно обратное распространение.
- [Научная статья: "SmoothQuant: Accurate and Efficient Post-Training Quantization for Large Language Models", Xiao et al., 2022](https://arxiv.org/abs/2211.10438)
  Переносит выбросы активаций в веса математически эквивалентным масштабом по каналам, что делает возможным W8A8. Использовать для: квантизации весов и активаций в 8 битах.
- [Научная статья: "QuaRot: Outlier-Free 4-Bit Inference in Rotated LLMs", Ashkboos et al., 2024](https://arxiv.org/abs/2404.00456)
  Поворачивает скрытые состояния преобразованиями Адамара, так что веса, активации и KV-кеш квантизуются в 4 бита. Использовать для: того, как повороты убирают выбросы.
- [Научная статья: "SpinQuant: LLM Quantization with Learned Rotations", Liu et al., 2024](https://arxiv.org/abs/2405.16406)
  Обучает матрицы поворота вместо того, чтобы фиксировать их, и показывает, что качество случайных поворотов сильно различается. Использовать для: того, почему важен выбор поворота.
- [Научная статья: "KIVI: A Tuning-Free Asymmetric 2bit Quantization for KV Cache", Liu et al., 2024](https://arxiv.org/abs/2402.02750)
  Находит, что ключи нужно квантизовать по каналам, а значения по токенам, и делает и то и другое в 2 битах. Использовать для: выбора оси при квантизации KV-кеша.
- [Научная статья: "KVQuant: Towards 10 Million Context Length LLM Inference with KV Cache Quantization", Hooper et al., 2024](https://arxiv.org/abs/2401.18079)
  Квантизация ключей по каналам до ротационного эмбеддинга, неравномерные типы и обработка выбросов для очень длинных контекстов. Использовать для: того, что квантизация KV-кеша даёт на длинном контексте.
- [Репозиторий: gptq, IST-DASLab](https://github.com/IST-DASLab/gptq)
  Эталонная реализация авторов GPTQ, README которой описывает `--act-order` (квантизовать столбцы в порядке убывания размера активаций), `--true-sequential` и `--static-groups`. Использовать для: act-order и тензора `g_idx`, которых в статье нет.

### Обучение с учётом квантизации

- [Научная статья: "Estimating or Propagating Gradients Through Stochastic Neurons for Conditional Computation", Bengio et al., 2013](https://arxiv.org/abs/1308.3432)
  Вводит и сравнивает оценщики градиентов через жёсткие пороги, включая straight-through estimator. Использовать для: происхождения STE.
- [Научная статья: "LLM-QAT: Data-Free Quantization Aware Training for Large Language Models", Liu et al., 2023](https://arxiv.org/abs/2305.17888)
  QAT на LLM с данными, которые модель порождает сама, включая квантизацию KV-кеша, в сравнении с PTQ в 4 битах. Использовать для: того, что QAT возвращает на LLM и какой ценой.
- [Научная статья: "QLoRA: Efficient Finetuning of Quantized LLMs", Dettmers et al., 2023](https://arxiv.org/abs/2305.14314)
  NF4, двойная квантизация и обучение адаптеров поверх замороженной 4-битной базы. Использовать для: границы с QAT и источника, по которому учит курс по дообучению.
- [Статья: "Quantization-Aware Training for Large Language Models with PyTorch", PyTorch Blog, 2024](https://pytorch.org/blog/quantization-aware-training/)
  Поток QAT в torchao на Llama 2 и Llama 3, с измеренным возвратом качества относительно PTQ и накладными расходами fake-квантизации на дообучении. Использовать для: того, что QAT возвращает и стоит на настоящей LLM, читая как измерения одной команды.

### Оборудование и обслуживание

- [Научная статья: "MARLIN: Mixed-Precision Auto-Regressive Parallel Inference on Large Language Models", Frantar et al., 2024](https://arxiv.org/abs/2408.11743)
  Ядро GPU с 4-битными весами и 16-битными активациями и анализ того, когда квантизация одних весов ускоряет пакетное декодирование. Использовать для: того, почему ускорение зависит от размера батча.
- [Научная статья: "QServe: W4A8KV4 Quantization and System Co-design for Efficient LLM Serving", Lin et al., 2024](https://arxiv.org/abs/2405.04532)
  Показывает, что накладные расходы на деквантизацию могут свести на нет выигрыш 4-битных схем на GPU, и совместно проектирует формат и ядро, чтобы их избежать. Использовать для: того, почему меньше бит не значит автоматически быстрее.
- [Документация: "Quantization", vLLM](https://docs.vllm.ai/en/latest/features/quantization/)
  Схемы, которые поддерживает один движок обслуживания, и на каком оборудовании. Использовать для: проверки, есть ли у схемы ядро, до того как её выбирать.
- [Документация: "Quantized KV Cache", vLLM](https://docs.vllm.ai/en/latest/features/quantization/quantized_kvcache/)
  KV-кеш в fp8: масштабы на тензор или на голову, масштабы по умолчанию без калибровки и их калибровка с помощью llm-compressor. Использовать для: того, что 8-битному KV-кешу нужно на практике.
- [Документация: "Quantization overview", Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/quantization/overview)
  Бэкенды квантизации, которые интегрирует Transformers, и как выбирать между ними. Использовать для: карты инструментов.
- [Репозиторий: llm-compressor, vLLM project](https://github.com/vllm-project/llm-compressor)
  Библиотека, которая применяет рецепты GPTQ, AWQ, SmoothQuant и FP8 и пишет чекпоинты, загружаемые vLLM. Использовать для: сквозного запуска PTQ на настоящей модели.
- [Репозиторий: compressed-tensors, Neural Magic](https://github.com/neuralmagic/compressed-tensors)
  Расширение safetensors, которое записывает схему квантизации чекпоинта в его конфигурацию. Использовать для: того, что хранит квантизованный чекпоинт safetensors.
- [Документация: "int8 W8A8" example, llm-compressor](https://github.com/vllm-project/llm-compressor/blob/main/examples/quantization_w8a8_int8/README.md)
  Разобранный рецепт W8A8 int8: сначала SmoothQuant, затем GPTQ с масштабами весов по каналам, затем динамические масштабы активаций на токен. Использовать для: запуска SmoothQuant на настоящей модели.
- [Документация: "Choosing a dataset", LLM Compressor](https://docs.vllm.ai/projects/llm-compressor/en/latest/steps/choosing-dataset/)
  Каким алгоритмам нужен калибровочный набор, как подобрать его предметную область под целевое применение и типичные размеры. Использовать для: практических советов по калибровочному набору.
- [Документация: "GPTQ", Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/quantization/gptq)
  Запуск GPTQ через `GPTQConfig` со встроенным датасетом или собственным текстом. Использовать для: квантизации GPTQ из Transformers.
- [Документация: "AWQ", Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/quantization/awq)
  Загрузка чекпоинтов AWQ и ключи `quantization_config`, которые записывает чекпоинт AWQ. Использовать для: чтения конфигурации чекпоинта AWQ.
- [Документация: "bitsandbytes", Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/quantization/bitsandbytes)
  Как Transformers загружает 8- и 4-битные модели bitsandbytes, включая тип данных для вычислений. Использовать для: того, чтобы увидеть, что хранимые 4-битные веса вычисляются в более высокой точности.
- [Документация: "NVIDIA A100 Tensor Core GPU" datasheet, NVIDIA](https://www.nvidia.com/content/dam/en-zz/Solutions/Data-Center/a100/pdf/nvidia-a100-datasheet-nvidia-us-2188504-web.pdf)
  Пропускная способность тензорных ядер A100 по форматам и её пропускная способность памяти. Использовать для: чисел Ampere в roofline-модели, читая как документацию производителя.
- [Документация: "NVIDIA Ada GPU Architecture" whitepaper, NVIDIA](https://images.nvidia.com/aem-dam/Solutions/Data-Center/l4/nvidia-ada-gpu-architecture-whitepaper-v2.1.pdf)
  Тензорные ядра Ada и их поддержка FP8. Использовать для: того, у каких GPU для инференса есть тензорные ядра FP8, читая как документацию производителя.
- [Документация: "NVIDIA H100 Tensor Core GPU", NVIDIA](https://www.nvidia.com/en-us/data-center/h100/)
  Таблица характеристик H100 со строками тензорных ядер FP8 и INT8 и пропускной способностью памяти. Использовать для: цифр Hopper, читая как документацию производителя.
- [Статья: "NVIDIA Hopper Architecture In-Depth", NVIDIA Technical Blog](https://developer.nvidia.com/blog/nvidia-hopper-architecture-in-depth/)
  Тензорные ядра FP8 и Transformer Engine, появившиеся вместе с Hopper. Использовать для: того, когда вычисления FP8 появились в GPU NVIDIA для дата-центров, читая как документацию производителя.

### Форматы файлов

- [Документация: "Safetensors", Hugging Face](https://huggingface.co/docs/safetensors/index)
  Формат файла тензоров, в котором поставляется большинство чекпоинтов, и что он хранит, а что нет. Использовать для: контейнера, рядом с которым лежит конфигурация квантизации.
- [Документация: "GGUF", Hugging Face Hub](https://huggingface.co/docs/hub/gguf)
  Обзор формата GGUF и таблица его типов квантизации с их раскладкой по битам. Использовать для: расшифровки имени типа GGUF.
- [Документация: llama.cpp quantize tool README, ggml-org](https://github.com/ggml-org/llama.cpp/blob/master/tools/quantize/README.md)
  Как llama.cpp преобразует модель в свои типы квантизации, список типов и как передаётся матрица важности. Использовать для: самостоятельного получения квантизации GGUF.
- [Репозиторий: safetensors, Hugging Face](https://github.com/huggingface/safetensors)
  Формат на уровне байтов: 8-байтовая длина заголовка в порядке little-endian, JSON-заголовок с именами, типами, формами и смещениями, затем данные. Использовать для: чтения заголовка чекпоинта без загрузки его тензоров.
- [Документация: "compressed-tensors", Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/quantization/compressed_tensors)
  Загрузка чекпоинтов compressed-tensors, с примером `config_groups` для FP8 и перечнем тензоров. Использовать для: чтения конфигурации compressed-tensors и её тензоров масштабов.
- [Карточка модели: "TinyLlama-1.1B-Chat-v1.0-GPTQ", TheBloke](https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GPTQ)
  Небольшой публичный 4-битный чекпоинт GPTQ, карточка которого объясняет разрядность, размер группы, act order и демпфирование. Использовать для: настоящего чекпоинта, который можно изучить.
- [Исходный код: ggml-common.h, ggml-org](https://github.com/ggml-org/llama.cpp/blob/master/ggml/src/ggml-common.h)
  Структура на C для каждого блочного типа GGUF. Использовать для: вывода числа бит на вес типа из его раскладки, а не цитирования.
- [Pull request: "k-quants", ikawrakow, llama.cpp, 2023](https://github.com/ggml-org/llama.cpp/pull/1684)
  Вводит k-кванты, именование type-0 и type-1 и исходные смеси S, M и L. Использовать для: того, что значили суффиксы, когда их ввели.
- [Pull request: "Importance Matrix calculation", ikawrakow, llama.cpp, 2024](https://github.com/ggml-org/llama.cpp/pull/4861)
  Выводит матрицу важности из активаций на калибровочном тексте и использует её, чтобы взвесить ошибку округления. Использовать для: того, почему матрица важности это калибровочный набор.
- [Документация: llama.cpp imatrix tool README, ggml-org](https://github.com/ggml-org/llama.cpp/blob/master/tools/imatrix/README.md)
  Как вычислить матрицу важности и передать её инструменту quantize. Использовать для: самостоятельного получения такой матрицы.

### Измерение потери качества

- [Научная статья: "Accuracy is Not All You Need", Dutta et al., 2024](https://arxiv.org/abs/2407.09141)
  Показывает, что квантизованная модель может совпадать с базовой по точности, меняя при этом многие отдельные ответы, и предлагает флипы и KL-дивергенцию как метрики расстояния. Использовать для: того, почему неизменное среднее может скрывать изменившуюся модель.
- [Научная статья: "Give Me BF16 or Give Me Death? Accuracy-Performance Trade-Offs in LLM Quantization", Kurtic et al., 2024](https://arxiv.org/abs/2411.02355)
  Более полумиллиона замеров схем FP8, INT8 и INT4 на моделях Llama 3.1 разных размеров и на разных задачах, с рекомендациями по развёртыванию для каждой схемы. Использовать для: того, чего стоит каждая схема, измеренного аккуратно.
- [Научная статья: "Scaling Laws for Precision", Kumar et al., 2024](https://arxiv.org/abs/2411.04330)
  Находит, что посттренировочная квантизация портит модель тем сильнее, чем больше данных на ней обучали. Использовать для: того, почему обычный ответ про 4 бита может не сработать на сильно обученной модели.
- [Репозиторий: lm-evaluation-harness, EleutherAI](https://github.com/EleutherAI/lm-evaluation-harness)
  Обвязка, с которой большинство статей о квантизации сообщает точность на задачах. Использовать для: запуска одних и тех же задач на базовой и на квантизованной модели.
- [Документация: "Perplexity of fixed-length models", Hugging Face Transformers](https://huggingface.co/docs/transformers/main/en/perplexity)
  Как перплексия вычисляется скользящим окном и почему окно меняет число. Использовать для: вычисления перплексии так, чтобы два запуска были сравнимы.
- [Научная статья: "Quantization Hurts Reasoning? An Empirical Study on Quantized Reasoning Models", Liu et al., 2025](https://arxiv.org/abs/2504.04823)
  Квантизованные рассуждающие модели при квантизации весов, KV-кеша и активаций на бенчмарках по математике, естественным наукам и коду; находит, что W8A8 и W4A16 могут быть без потерь, а меньшая разрядность рискованна. Использовать для: того, выполняется ли обычный ответ про 4 бита для рассуждающей модели.
- [Документация: llama.cpp perplexity tool README, ggml-org](https://github.com/ggml-org/llama.cpp/blob/master/tools/perplexity/README.md)
  Статистики перплексии, KL-дивергенции и совпадения по лучшему токену относительно 16-битных логитов, с таблицей типов GGUF. Использовать для: измерения квантизованной GGUF относительно базовой модели сверх перплексии.

## Пробелы

- Нет единой нейтральной к производителям актуальной таблицы того, какие поколения GPU вычисляют нативно в каких форматах. Урок 20 опирается на страницы производителей и на матрицы поддержки движков обслуживания, которые меняются с каждым выпуском.
