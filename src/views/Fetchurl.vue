<template>
  <div v-if="!currentUser" class="pt-2 page-fetch-url">
    <Header1 id="page-title" class="page-fetch-url-heading" text="Authorized users only" />
    <form class="bg-transparent border-0 canvas-form" @submit.prevent="casLogin">
      <div class="d-flex w-100">
                <v-btn
                  id="cas-login-btn"
                  class="text-no-wrap my-2"
                  color="primary"
                  type="submit"
                >
                  <span>Sign In via CAS</span>
                </v-btn>
      </div>
    </form>
  </div>
  <div v-if="currentUser" class="pt-2">
    <form class="bg-transparent border-0 canvas-form" @submit.prevent="logOut">
      <div class="d-flex w-100">
                <v-btn
                  id="cas-logout-btn"
                  class="text-no-wrap my-2"
                  color="primary"
                  type="submit"
                >
                  <span>Log Out {{ currentUser.uid }}</span>
                </v-btn>
      </div>
    </form>
    <div v-if="!isLoading" class="page-fetch-url">
      <Header1 id="page-title" class="page-fetch-url-heading" text="Generate DataHub archive recovery URL" />
        <form class="bg-transparent border-0 canvas-form" @submit.prevent="fetchUrl">
          <v-row no-gutters>
            <label for="page-fetch-url-name" class="fetch-url-label mb-2 mt-3">
              Enter G&ZeroWidthSpace;C&ZeroWidthSpace;P storage object URL
            </label>
            <textarea
              id="page-fetch-url-name"
              v-model="gsSourceUrl"
              :disabled="isRequesting"
              placeholder="gs://ucb-datahub-archived-homedirs/2022-2-summer/data100/.....tar.gz"
              rows="4"
              required
              @focus="clearContents"
            ></textarea>
          </v-row>

          <v-row no-gutters> 
            <v-col cols="12">
              <div class="d-flex justify-end w-100">
                <v-btn
                  id="generate-url-btn"
                  aria-describedby="fetch-url-progress"
                  :aria-disabled="importButtonDisabled"
                  class="text-no-wrap my-2"
                  color="primary"
                  :disabled="importButtonDisabled"
                  type="submit"
                >
                  <span v-if="!isRequesting">Generate 7-day archive download URL</span>
                  <span v-if="isRequesting">
                    <SpinnerWithinButton /> Generating 7-day archive download URL...
                  </span>
                </v-btn>
                <span id="fetch-url-progress" class="sr-only" role="status">
                  <span v-if="isRequesting">Importing Users</span>
                </span>
              </div>
          </v-col>

          </v-row>
        </form>
        


        <div v-if="wasCreated" class="d-flex">
          <div>
            <label for="response-from-gcp" class="fetch-url-label mb-2 mt-3">
              Success: the following 7-day download U&ZeroWidthSpace;R&ZeroWidthSpace;L was created.
            </label>
            <v-text-field id="response-from-gcp" v-model="responseFromGcp" readonly />
            <form class="bg-transparent border-0 canvas-form" @submit.prevent="copyText">
              <v-btn
                    id="copyText"
                    class="text-no-wrap my-2"
                    color="primary"
                    type="submit"
              >
                  <span>Copy this URL to your clipboard</span>
              </v-btn>
            </form>
            </div>
          



        </div>

        <div v-if="failedCreate" class="d-flex">
          <v-icon class="icon-green mr-2" :icon="mdiCheckCircle" />
          <div>
            <strong>
              {{ responseFromGcp }}
            </strong>
          </div>
        </div>



    </div>

  </div>



</template>

<script>
import Context from '@/mixins/Context'
import {getCasLoginURL, getCasLogoutURL} from '@/api/user'
import {fetchUrl} from '@/api/fetch-url'
import Header1 from '@/components/utils/Header1.vue'

export default {
  name: 'Login',
  mixins: [Context],
  data: () => ({
    gsSourceUrl: undefined,
    responseFromGcp: undefined,
    isRequesting: undefined,
    wasCreated: undefined,
    failedCreate: undefined
  }),
  components: {Header1},
  methods: {
    toFetchUrl() {
      window.location.href = `http://localhost:8080/fetchurl`
    },
    casLogin() {
      getCasLoginURL().then(data => window.location = data.casLoginURL)
    },
    logOut() {
      getCasLogoutURL().then(data => window.location.href = data.casLogoutURL)
    },
    fetchUrl() {
      this.isRequesting = true
      fetchUrl(this.gsSourceUrl).then(data => {
        this.isRequesting = false
        if (data.status == "success") {
          this.wasCreated = true
          this.failedCreate = false
        } else {
          this.wasCreated = false
          this.failedCreate = true
        }
        this.responseFromGcp = data.response
      })
      isRequesting = false
    },
    copyText() {
      navigator.clipboard.writeText(this.responseFromGcp);
    },
    clearContents() {
      this.gsSourceUrl = '';
      this.responseFromGcp = '';
    }
  }
}
</script>


<style scoped lang="scss">
.page-fetch-url {
  color: $color-off-black;
  font-family: $body-font-family;
  font-size: 14px;
  font-weight: 300;
  padding: 10px 20px;
  .page-fetch-url-heading {
    font-family: $body-font-family;
    font-size: 23px;
    font-weight: normal;
    margin: 10px 0;
  }
  .fetch-url-label {
    font-weight: 400;
  }
}
</style>