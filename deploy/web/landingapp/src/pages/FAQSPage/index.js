/*****
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";
import { Link, useHistory } from "react-router-dom";

const FAQSPage = () => {
  let history = useHistory();
  return (
    <div className="__faqspage-container__ w-screen h-screen">
      <div className="w-full flex flex-start">
        <div
          className=" text-white cursor-pointer hover:text-green-100 p-4 text-2xl"
          onClick={() => history.goBack()}
        >
          Back
        </div>
      </div>
      <div className="__faqspage-body__ flex flex-col items-center w-full h-full text-white overflow-y-scroll">
        <div className="__faqspage-copy__ w-3/5 mb-26">
          <div className="__faqspage-header_container__ flex justify-center items-center">
            <h1 className="__faqspage-header_text__ text-white font-extrabold text-6xl">
              LIGHT FAQ
            </h1>
          </div>
          <div className="__internalcontext-container__ bg-blue-400 border-black border-4 p-6">
            <p className="mb-4">
              <span className="font-bold"> Meta-internal context: </span>
              The FAIR Labs Dialogue research group has approval (LAMA,
              director) to release our LIGHT chatbot to the public as a
              multiplayer chat game where players and bots interact within a
              shared fantasy world. The primary goal of the demo will be to
              drive conversational research outcomes. Specifically, this setting
              provides rich grounded dialogue (tied to the fantasy world),
              multiparty interaction, human-human dialogue, dialogue + action
              episodes, and goal-driven interactions, all extending the standard
              interaction type and model feedback we get in other bots like
              BlenderBot. The team will release this specifically via targeted
              FB ads for users who have shown interest in fantasy games, role
              playing games, interactive fiction, and similar categories.
              Previously, the team released single-player versions of the game
              on Messenger in the past, and this release is the culmination of
              what the project has been trying to establish.
            </p>
            <p className="mb-4">
              The following FAQ will live on the LIGHT demo website (currently
              accessible on VPN only). The landing page also contains a
              checklist of acknowledgements, such as the user knows the bot may
              say unsafe things, the user knows we will save conversational data
              for research purposes, and links to our terms of service and
              privacy policy being prepared by Legal. Users must acknowledge all
              terms of use before they are able to interact with the bot.
            </p>
            <p className="mb-4">
              We’re using this FAQ as a form of “reactive comms” for our initial
              beta deploy of the demo. The audience of the FAQ is the users, who
              will be several thousand people from the general, 18+ US public,
              sourced by Facebook ads. This FAQ will also be used for media
              reactively should they inquire about LIGHT. Later on (TBD 2023) we
              hope to do a broader public deployment with proactive comms, and
              at that point this FAQ will be seen by a larger audience.
            </p>
          </div>
          <div className="__about-container__ text-white">
            <h4 className="font-bold underline">About LIGHT</h4>
            <p className="mb-4">
              LIGHT is a research project by Meta AI. Our main goal in this
              research demo is to progress interactive AI research by making
              models more able to understand context, which means making
              artificial intelligence (AI)-based dialogue systems better for
              everyone who uses them. In this project, we are providing an
              environment for our best dialogue research prototypes to interact
              with players in a shared context, and asking players to help
              contribute by interacting with the bots and each other and sharing
              feedback on their interactions.
            </p>
            <p className="mb-4">
              Users should be aware that despite our best attempts to reduce
              such issues, AI agents and other players may be inappropriate,
              rude, or make untrue or contradictory statements. Comments stated
              in LIGHT are not representative of Meta’s views as a company, and
              should not be relied on for factual information, including but not
              limited to medical, legal, or financial advice. Users must be at
              least 18 years old (or, if higher than 18, the age of majority in
              the jurisdiction from which you are accessing LIGHT), must reside
              in the United States, and must have agreed to be bound by the{" "}
              <Link
                to="terms"
                className="text-blue-500 cursor-pointer underline hover:text-green-100"
              >
                Supplemental LIGHT Terms of Service
              </Link>
              .
            </p>
            <p className="mb-4">
              Please also ensure that you do not include any personal
              information in your conversations, such as names, phone numbers,
              addresses, birthdays, and emails. We will make our best effort to
              de-identify any personal information from the conversations, but
              are using an automated process that may not be 100% effective. We
              plan to regularly release de-identified data collected from within
              LIGHT, with the goal of enabling other researchers to extend upon
              our work, and this will be available for download from our{" "}
              <a
                target="_blank"
                className="text-blue-500 cursor-pointer underline hover:text-green-100"
                href="https://parl.ai/projects/light/"
              >
                project page
              </a>
              . The complete source code for the project will be made available
              on our github.
            </p>
          </div>
          <div className="__faq-container__ text-white">
            <h4 className="font-bold underline">FAQ</h4>
            <h5 className="font-bold ">What is LIGHT?</h5>
            <p className="mb-4">
              LIGHT is a research project focused on creating realistic
              interactive AI, set in a multiplayer fantasy text adventure game.
              LIGHT stands for “Learning in Interactive Games with Humans and
              Text.” The LIGHT game is a direct application of our research, and
              also stands as a live environment to allow players to interact
              with models and other players directly.
            </p>
            <h5 className="font-bold ">What is the goal of LIGHT?</h5>
            <p className="mb-4">
              Most dialogue research at the moment is either 2-person
              open-domain conversation mostly detached from explicit context, or
              task-oriented and discussing very specific goals. By creating a
              complete environment with soft goals and visible context, we
              bridge these two and create a dataset that is valuable for
              understanding how to make AI models understand goals and context.
            </p>
            <p className="mb-4">
              We believe that by collecting gameplay interactions between people
              and the best agents we have, set in an environment where we know
              the context they’re discussing, we can train better agents that
              understand context, follow stories, and create meaningful
              experiences for players. We also believe that by publishing the
              datasets and results, we can provide valuable data for other
              researchers to make advancements in the field of AI-based dialogue
              systems.
            </p>
            <h5 className="font-bold ">What is the value of this work?</h5>
            <p className="mb-4">
              Many people already interact with chatbots via voice assistants
              and in various customer service situations. In the future, it is
              likely humans will spend even more time interacting with helpful
              chatbots and that these chatbots will need to sound increasingly
              human-like to be useful. They will also need to know when
              conversational or local information is relevant. As you can see
              from interacting with agents in LIGHT, we have a long way to go
              before chatbots can reach human-levels of conversation. This
              deployment and our ongoing research will help improve the safety
              and quality of chatbots over time.
            </p>
            <h5 className="font-bold ">
              How does the bot work and what information is it accessing to
              converse?
            </h5>
            <p className="mb-4">
              LIGHT agents are based on a large language model trained on
              publicly available text data. These include knowledge-grounded
              datasets like Wizard of the Internet, QA datasets like Natural
              Questions and Open-Domain Dialogue datasets like the Blended Skill
              Talk are then fine-tuned on the fantasy text conversation datasets
              noted on our{" "}
              <a
                target="_blank"
                className="text-blue-500 cursor-pointer underline hover:text-green-100 "
                href="https://parl.ai/projects/light/"
              >
                project page
              </a>
              . A complete list of the datasets used in pretraining is available
              in the{" "}
              <a
                target="_blank"
                className="text-blue-500 cursor-pointer underline hover:text-green-100 "
                href="https://github.com/facebookresearch/ParlAI/blob/main/parlai/zoo/bb3/model_card.md"
              >
                BlenderBot3 model card
              </a>
              .
            </p>
            <p>
              We are committed to making our work transparent and easy for
              others to reproduce and build upon, so you can also find links to
              publications, models, and datasets on our{" "}
              <a
                target="_blank"
                className="cursor-pointer text-blue-500 underline hover:text-green-100"
                href="https://parl.ai/projects/light/"
              >
                project page
              </a>
              .
            </p>
            <h5 className="font-bold ">
              Will Meta have access to my personal data? What data is saved and
              for how long? Who will have access to the data?
            </h5>
            <p className="mb-4">
              We collect technical information about your browser or device,
              including through the use of cookies, but we use that information
              only to provide the tool and for analytics purposes to see how
              individuals interact on our website.
            </p>
            <p className="mb-4">
              In playing on LIGHT, users agree to sharing their conversations
              with LIGHT for research purposes when they login on the LIGHT
              website. We will store the text of the interactions made in LIGHT
              worlds indefinitely, and eventually may release it as part of a
              public data set. If we publicly release a data set of contributed
              conversations, the publicly released dataset will not associate
              contributed conversations with the contributor’s name, login
              credentials, browser or device data, or any other personally
              identifiable information. Please be sure you are okay with how
              we’ll use interactions as specified below before you consent to
              contributing to research.
            </p>
            <p className="mb-4">
              If you agree to contributing your conversation to further research
              by logging in on the LIGHT website, your in-game interactions may
              be used, released, or published for any of the following purposes:
            </p>
            <ul className="flex justify-start items-start flex-col list-disc pl-7">
              <li className="mb-4">
                To train a model to improve conversational abilities
              </li>
              <li className="mb-4">
                To ensure quality annotations by human viewers
              </li>
              <li className="mb-4">
                As part of an academic research paper or video
              </li>
              <li className="mb-4">
                As part of a publicly available database for researchers to
                develop language-generation models; and/or
              </li>
              <li className="mb-4">
                As part of future initiatives to encourage additional
                interaction collection.
              </li>
            </ul>
            <p className="mb-4">
              Please also ensure that you do not include any personally
              identifiable information in the content of your conversations,
              such as names, phone numbers, addresses, birthdays, and emails. We
              will make our best effort to de-identify any personal information
              from the conversations, but are using an automated process that
              may not be 100% effective.
            </p>
            <p className="mb-4">
              If a user would like to interact with LIGHT without having the
              conversation used for research, they should either follow the
              project for information on when collection-free worlds launch, or
              can directly interact with LIGHT locally by using the code
              available on our{" "}
              <a
                target="_blank"
                className="text-blue-500 cursor-pointer underline hover:text-green-100"
                href="https://github.com/facebookresearch/LIGHT/tree/main/deploy/web"
              >
                git repository
              </a>
              .
            </p>
            <p className="mb-4">
              Also see the{" "}
              <Link
                to="terms"
                className="text-blue-500 cursor-pointer underline hover:text-green-100"
              >
                Supplemental LIGHT Terms of Service
              </Link>{" "}
              and Meta Platform, Inc.'s Data Policy (available at{" "}
              <a
                target="_blank"
                className="text-blue-500 cursor-pointer underline hover:text-green-100 "
                href="https://www.facebook.com/about/privacy/update"
              >
                https://www.facebook.com/about/privacy/update
              </a>
              ).
            </p>
            <h5 className="font-bold ">
              How does LIGHT handle safety against offensive content?
            </h5>
            <p className="mb-4">
              We take safety very seriously. We have conducted extensive
              research on dialogue safety and made attempts to reduce the
              possibility that our bot engages in conversations that reflect
              demographic bias or stereotypes. We have also worked to minimize
              the bots’ use of vulgar language, slurs, and culturally
              insensitive comments. We have further worked to hide content that
              is sent to LIGHT but referring to real-world scenarios or context,
              as this aligns with both preventing content sent to LIGHT from
              being offensive and harmful and our research goals for having
              LIGHT interactions be about LIGHT context. This attempts to
              prevent players from being exposed to harmful messages sent by
              other players. On top of domain filtering, we rely on the same
              state of the art safety methods employed for BlenderBot 3,
              including baked-in safety and robustness to adversarial prompts
              attempting to elicit negative responses. Our research shows that
              these approaches outperform existing techniques.
            </p>
            <p className="mb-4">
              However, despite all the work that has been done, we recognize
              that models in LIGHT can still say things we are not proud of.
              This is all the more reason to bring the research community in.
              Without direct access to these models, researchers are limited in
              their ability to design detection and mitigation strategies.
            </p>
            <h5 className="font-bold ">
              What happens if something offensive is said in LIGHT (by humans or
              bots) despite your safety efforts?
            </h5>
            <p className="mb-4">
              If any agent in LIGHT says something offensive, the user should
              report the message by clicking the “thumbs down” beside the
              message and selecting “Inappropriate or Harmful” as the reason for
              the dislike. We will use this feedback to improve future
              iterations of the bot, and to improve our filters for
              objectionable content by players. Note that bot and human agents
              may say things that are “abrasive” or “mean”, but often this is
              related to the persona they are portraying. If you feel these
              statements go too far, feel free to mark as “Inappropriate or
              Harmful”, or if they don’t make sense in context mark as “Out of
              Character”.
            </p>
            <h5 className="font-bold ">
              Does the bot ever say anything untrue?
            </h5>
            <p className="mb-4">
              Unfortunately yes, LIGHT agents can make false or contradictory
              statements. Users should not rely on LIGHT for factual
              information, including but not limited to medical, legal, or
              financial advice. While we try to prevent LIGHT agents from even
              talking about these spaces, they may still attempt to.
            </p>
            <p className="mb-4">
              In research, we say that models like the one that powers LIGHT
              have "hallucinations", where the bot confidently says something
              that is not true. Bots can also misremember details of the current
              conversation, and even forget that they are a bot.
            </p>
            <p className="mb-4">
              While we work on this area, please help us improve by selecting
              the “thumbs down” button by any untrue or confusing messages sent
              by the bot.
            </p>
            <h5 className="font-bold ">
              How do I know if I’m talking to a bot or another human?
            </h5>
            <p className="mb-4">
              Inside the LIGHT game we don’t currently distinguish between bot
              and human responses.
            </p>
            <h5 className="font-bold ">
              What languages does this bot support? Is it English-only?
            </h5>
            <p className="mb-4">
              Currently LIGHT is designed for English-only conversations.
              However, multilingual AI is a large and active research area for
              Meta, and we have made some exciting progress in the space. For
              example, see:
            </p>
            <ul className="flex justify-start items-start flex-col list-disc pl-7">
              <li className="mb-4">
                <a
                  target="_blank"
                  className="cursor-pointer text-blue-500 underline hover:text-green-100"
                  href="https://ai.facebook.com/blog/the-flores-101-data-set-helping-build-better-translation-systems-around-the-world/"
                >
                  The FLORES-101 data set: Helping build better translation
                  systems around the world{" "}
                </a>
              </li>
              <li className="mb-4">
                <a
                  target="_blank"
                  className="cursor-pointer text-blue-500 underline hover:text-green-100"
                >
                  A new open data set for multilingual speech research
                </a>
              </li>
              <li className="mb-4">
                <a
                  target="_blank"
                  className="cursor-pointer text-blue-500 underline hover:text-green-100"
                  href="https://ai.facebook.com/blog/the-first-ever-multilingual-model-to-win-wmt-beating-out-bilingual-models/"
                >
                  {" "}
                  The first-ever multilingual model to win WMT, beating out
                  bilingual models{" "}
                </a>
              </li>
              <li className="mb-4">
                <a
                  target="_blank"
                  className="cursor-pointer text-blue-500 underline hover:text-green-100"
                  href="https://ai.facebook.com/blog/nllb-200-high-quality-machine-translation/"
                >
                  200 languages within a single AI model: A breakthrough in
                  high-quality machine translation
                </a>
              </li>
            </ul>
            <p className="mb-4">
              Some day, we hope to connect these works and build multilingual
              experiences.
            </p>
            <h5 className="font-bold">
              Does Meta plan to open source the model and code for LIGHT?
            </h5>
            <p className="mb-4">
              We plan to open source all of the code components of the LIGHT
              setup as well as all dialogue, action, and world-generation
              models. These will be made available on our{" "}
              <a
                target="_blank"
                className="cursor-pointer text-blue-500 underline hover:text-green-100"
                href="https://github.com/facebookresearch/LIGHT"
              >
                github repository
              </a>
              .
            </p>
            <h5 className="font-bold">
              Will Meta open source the data collected from this bot?{" "}
            </h5>
            <p className="mb-4">
              We intend to open source the collected LIGHT data regularly.
            </p>
            <h5 className="font-bold">
              Does Meta plan to use this bot in a product?
            </h5>
            <p className="mb-4">
              LIGHT, which is still a work in progress, is currently used for
              research only.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FAQSPage;
