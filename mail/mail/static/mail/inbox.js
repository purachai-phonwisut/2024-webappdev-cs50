document.addEventListener('DOMContentLoaded', function() {

  // toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);
  document.querySelector('#compose-form').addEventListener('submit',send_email);
  window.addEventListener('popstate', function(event) {
    if (event.state && event.state.mailbox) {
      load_mailbox(event.state.mailbox);
    } else {
      // Default to inbox or any other default state
      load_mailbox('inbox');
    }
  });
  load_mailbox('inbox');
});

function load_mailbox(mailbox) {

  window.history.pushState({mailbox: mailbox}, "", `#${mailbox}`);

  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#get-email').innerHTML = '';
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  fetch(`/emails/${mailbox}`, {
    method: 'GET',
  })
  .then(response => response.json())
  .then(emails => {
    const email_view = document.getElementById('emails-view');

    emails.forEach(item => {
      let shouldShow = false;
      let buttonText = '';
      if (mailbox === 'archive') {
        shouldShow = item.archived;
        buttonText = 'Unarchive';
      } else if (mailbox === 'inbox') {
        shouldShow = !item.archived;
        buttonText = 'Archive';
      } else if (mailbox === 'sent') {
        shouldShow = true;
      }

      if (shouldShow) {
        const email_div = document.createElement('div');
        email_div.className = 'email-summary ' + (item.read ? 'email-item-container-read' : 'email-item-container-unread');
        const mailListContainer = document.createElement('div');
        mailListContainer.className = 'mail-list-container';

        mailListContainer.innerHTML = `
          <span class="mail-float-start">${item.sender}</span>
          <span class="mail-float-mid">${item.subject}</span>
          <span class="mail-float-end">${item.timestamp}</span>
        `;

        if (mailbox === 'inbox' || mailbox === 'archive') {
          const button = document.createElement('button');
          button.textContent = buttonText;
          button.className = 'mail-archive-button'; // Assign a class for styling
          button.addEventListener('click', (e) => {
            e.stopPropagation();
            toggleArchiveStatus(item.id, item.archived);
          });
          mailListContainer.appendChild(button);
        }

        email_div.appendChild(mailListContainer);
        email_div.addEventListener('click', () => get_email(item.id));
        email_view.appendChild(email_div);
      }
    });
  });
}


function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';
  document.querySelector('#get-email').innerHTML = '';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
}

function send_email(event) {

  event.preventDefault();
  let body = document.querySelector('#compose-body').value
  let recipients = document.querySelector('#compose-recipients').value
  let subject = document.querySelector('#compose-subject').value

  fetch('/emails', {
    method: 'POST',
    body: JSON.stringify({
        recipients: recipients,
        subject: subject,
        body: body
    })
  })
  .then(response => response.json())
  .then(result => {
      // Print result
      console.log(result);
      load_mailbox('sent')
  });
}

function get_email(email_id) {

  document.querySelector('#emails-view').style.display = 'none';
  fetch(`/emails/${email_id}`, {
  method: 'GET'
})
.then(response => response.json())
.then(email_id=> {console.log(email_id);
  return email_id;
  })
  
  .then(email => {
    const get_email = document.getElementById('get-email');
    get_email.innerHTML = `
    <div id="email-sender"><b>From:</b> ${email.sender}</div>
    <div id="email-recipients"><b>To:</b> ${email.recipients}</div>
    <div id="email-subject"><b>Subject:</b> ${email.subject}</div>

    <button class="reply-btn">Reply</button>
    <hr style="height:1px;border-width:0;color:gray;background-color:gray">

    <div id="email-body"><b>Body:</b> 
    ${email.body}</div>

    `
    document.querySelector('.reply-btn').addEventListener('click', () => reply_email(email));

  });

  fetch(`/emails/${email_id}`,{
    method: 'PUT',
    body : JSON.stringify({
      read:true
    })
    
  })
}

function toggleArchiveStatus(email_id, currentlyArchived) {
  fetch(`/emails/${email_id}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      archived: !currentlyArchived
    })
  })
  .then(response => {
    if (response.ok) {
      // Determine which mailbox to load based on the current archived status
      const mailboxToLoad = currentlyArchived ? 'archive' : 'inbox';
      load_mailbox(mailboxToLoad);
    } else {
      alert('There was an error updating the email.');
    }
  });
}

function reply_email(email) {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';
  document.querySelector('#get-email').innerHTML = '';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = `${email.sender}`;
  document.querySelector('#compose-subject').value = `Re: ${email.subject}`;
  document.querySelector('#compose-body').value = `On ${email.timestamp} ${email.sender} wrote:
  ${email.body}`;
}

function goBack() {
  window.history.back();
}
