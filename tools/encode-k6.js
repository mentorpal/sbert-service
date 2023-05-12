/*
 * This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
 * Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
 *
 * The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
 */
import http from "k6/http";
import { SharedArray } from "k6/data";
import { check } from "k6";
// "http://0.0.0.0:5000/v1/encode"
// "https://sbert-dev.mentorpal.org/v1/encode"
const apiUrl = "https://sbert-dev.mentorpal.org/v1/encode";
const questions = new SharedArray("user questions", function () {
  // subset of https://gist.github.com/khamer/66102c745a9a75de997c038e3166a95d
  return JSON.parse(open("./questions.json"));
});

const params = {
  headers: {
    'Authorization': `Bearer ${__ENV.API_KEY}`,
  },
};

export default function () {
  // randomly pick one mentor and question:
  const q = questions[Math.floor(Math.random() * questions.length)];
  const url = `${apiUrl}?query=${encodeURIComponent(q)}`;
  const req = http.get(url.toString(), params);

  check(req, {
    "is status 200": (r) => r.status === 200,
  });
  if (req.status === 200) {
    const res = req.json();
    // console.log(res.answer_text, q)
    check(res, {
      "has no errors": (r) => "errors" in r === false,
      //	    'has an answer': (r) => r.answer_text && r.answer_text.length > 2,
    });
  } else {
    console.log(req.status, req.text, req.body, q);
    console.log(url.toString());
  }
}
