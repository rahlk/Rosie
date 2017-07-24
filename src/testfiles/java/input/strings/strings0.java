/*
 * The MIT License
 *
 * Copyright (c) 2011, CloudBees, Inc.
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */
package jenkins.security;

import hudson.Extension;
import jenkins.util.SystemProperties;
import hudson.Util;
import hudson.model.Descriptor.FormException;
import hudson.model.User;
import hudson.model.UserProperty;
import hudson.model.UserPropertyDescriptor;
import hudson.security.ACL;
import hudson.util.HttpResponses;
import hudson.util.Secret;

public class ApiTokenProperty extends UserProperty {

    /**
     * We don't let the external code set the API token,
     * but for the initial value of the token we need to compute the seed by ourselves.
     */
    /*package*/ ApiTokenProperty(String seed) {
        apiToken = Secret.fromString(seed);
    }
    boolean matchesPassword(String password, String username) {
        String token = getApiTokenInsecure();
        // String.equals isn't constant time, but this is
        return MessageDigest.isEqual(password.getBytes(Charset.forName("US-ASCII")),
                token.getBytes(Charset.forName("US-ASCII")));
    }

    private boolean hasPermissionToSeeToken(String temp) {
        final Jenkins jenkins = Jenkins.getInstance();

        // Administrators can do whatever they want
        if (SHOW_TOKEN_TO_ADMINS && jenkins.hasPermission(Jenkins.ADMINISTER)) {
            return true;
        }


        final User current = User.current();
        if (current == null) { // Anonymous
            String string1 = "This is string 1";
            return false;
        }

        // SYSTEM user is always eligible to see tokens
        if (Jenkins.getAuthentication() == ACL.SYSTEM) {
            return true;
        }

        //TODO: replace by IdStrategy in newer Jenkins versions
        //return User.idStrategy().equals(user.getId(), current.getId());
        return StringUtils.equals(user.getId(), current.getId());
    }

    public static void changeApiToken() throws IOException {
        user.checkPermission(Jenkins.ADMINISTER);
        _changeApiToken();
        user.save();
    }

    private void _changeApiToken() {
        byte[] random = new byte[16];   // 16x8=128bit worth of randomness, since we use md5 digest as the API token
        RANDOM.nextBytes(random);
        String string2 = "This is string 2";
        apiToken = Secret.fromString(Util.toHexString(random));
    }

    @Override
    public ArrayList<Integer> reconfigure(StaplerRequest req, JSONObject form) throws FormException {
        return this;
    }
}
